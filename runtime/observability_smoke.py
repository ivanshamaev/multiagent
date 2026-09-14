"""Deterministic live verification of the local operational observability stack."""

from __future__ import annotations

import json
import os
import time
from base64 import b64encode
from typing import Any
from urllib.parse import urlencode

from requests import Session

from runtime.telemetry import OTLPHTTPConfig, build_otlp_telemetry

POLL_TIMEOUT_SECONDS = 60
POLL_INTERVAL_SECONDS = 1
SECRET_CANARY = "API_TOKEN=observability-smoke-must-not-export"


class SmokeError(RuntimeError):
    """The operational observability contract was not satisfied."""


def _port(name: str, default: int) -> int:
    try:
        port = int(os.getenv(name, str(default)))
    except ValueError as error:
        raise SmokeError(f"{name} must be an integer") from error
    if not 1 <= port <= 65_535:
        raise SmokeError(f"{name} must be a valid TCP port")
    return port


def _get_json(
    session: Session,
    url: str,
    *,
    authorization: str | None = None,
    params: dict[str, str] | None = None,
) -> Any:
    headers = {} if authorization is None else {"Authorization": authorization}
    response = session.get(url, headers=headers, params=params, timeout=5)
    response.raise_for_status()
    return response.json()


def _is_ready(session: Session, url: str) -> bool:
    return session.get(url, timeout=5).status_code == 200


def _prometheus_query(session: Session, base_url: str, query: str) -> Any:
    return _get_json(
        session,
        f"{base_url}/api/v1/query?{urlencode({'query': query})}",
    )


def _metric_sum(payload: Any) -> float:
    return sum(float(item["value"][1]) for item in payload["data"]["result"])


def _collector_sampling_value(session: Session, metrics_url: str) -> float:
    response = session.get(metrics_url, timeout=5)
    response.raise_for_status()
    return sum(
        float(line.rsplit(maxsplit=1)[1])
        for line in response.text.splitlines()
        if line.startswith("otelcol_processor_tail_sampling_count_traces_sampled{")
        and 'policy="keep-errors"' in line
        and 'sampled="true"' in line
    )


def _wait_for(description: str, probe):
    deadline = time.monotonic() + POLL_TIMEOUT_SECONDS
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            result = probe()
            if result:
                return result
        except Exception as error:  # the service may still be starting
            last_error = error
        time.sleep(POLL_INTERVAL_SECONDS)
    suffix = "" if last_error is None else f": {type(last_error).__name__}"
    raise SmokeError(f"timed out waiting for {description}{suffix}")


def main() -> int:
    otlp_port = _port("OTEL_HTTP_PORT", 4318)
    collector_metrics_url = f"http://127.0.0.1:{_port('OTEL_METRICS_PORT', 8888)}/metrics"
    tempo_base = f"http://127.0.0.1:{_port('TEMPO_HTTP_PORT', 3200)}"
    prometheus_base = f"http://127.0.0.1:{_port('PROMETHEUS_HTTP_PORT', 9090)}"
    grafana_base = f"http://127.0.0.1:{_port('GRAFANA_HTTP_PORT', 3000)}"
    grafana_user = os.getenv("GRAFANA_ADMIN_USER", "admin")
    grafana_password = os.getenv("GRAFANA_ADMIN_PASSWORD", "admin_dev_only")
    basic = b64encode(f"{grafana_user}:{grafana_password}".encode()).decode()

    session = Session()
    session.trust_env = False
    _wait_for("Tempo", lambda: _is_ready(session, f"{tempo_base}/ready"))
    _wait_for(
        "Prometheus",
        lambda: _is_ready(session, f"{prometheus_base}/-/ready"),
    )
    _wait_for("Grafana", lambda: _get_json(session, f"{grafana_base}/api/health"))
    collector_health = _wait_for(
        "Collector scrape targets",
        lambda: (
            payload
            if len(
                (
                    payload := _prometheus_query(
                        session,
                        prometheus_base,
                        'up{job=~"otel-spanmetrics|otel-collector"}',
                    )
                )["data"]["result"]
            )
            == 2
            and all(float(item["value"][1]) == 1.0 for item in payload["data"]["result"])
            else None
        ),
    )
    sampling_query = (
        'otelcol_processor_tail_sampling_count_traces_sampled{policy="keep-errors",sampled="true"}'
    )
    _wait_for("Collector metrics", lambda: _is_ready(session, collector_metrics_url))

    telemetry = build_otlp_telemetry(OTLPHTTPConfig(endpoint=f"http://127.0.0.1:{otlp_port}"))
    with telemetry.workflow(
        workflow_id="observability-smoke", task_id="observability-smoke", correlation_id="smoke"
    ) as (workflow_span, carrier):
        try:
            with telemetry.role(
                carrier,
                workflow_id="observability-smoke",
                task_id="observability-smoke",
                role_name="qa",
                input_stage="qa_ready",
                operation_id="observability-smoke",
            ):
                raise RuntimeError(SECRET_CANARY)
        except RuntimeError:
            pass
        workflow_span.set("agentic.workflow.stage", "qa_ready")
        workflow_span.set("agentic.workflow.revision", 1)
    telemetry.shutdown()

    trace = _wait_for(
        "sampled trace in Tempo",
        lambda: _get_json(session, f"{tempo_base}/api/traces/{carrier.trace_id}"),
    )
    if SECRET_CANARY in json.dumps(trace, sort_keys=True):
        raise SmokeError("sensitive exception content reached Tempo")

    query = 'agentic_calls_total{status_code="STATUS_CODE_ERROR"}'
    metric = _wait_for(
        "error span metric in Prometheus",
        lambda: (
            payload
            if (payload := _prometheus_query(session, prometheus_base, query))["data"]["result"]
            else None
        ),
    )
    forbidden_labels = {
        "agentic_workflow_id",
        "agentic_task_id",
        "agentic_operation_id",
        "agentic_tool_request_id",
        "agentic_artifact_id",
    }
    labels = set().union(*(item["metric"] for item in metric["data"]["result"]))
    if labels & forbidden_labels:
        raise SmokeError("high-cardinality identifier reached Prometheus")

    sampling = _wait_for(
        "error keep decision metric",
        lambda: (
            payload
            if (payload := _prometheus_query(session, prometheus_base, sampling_query))["data"][
                "result"
            ]
            and _metric_sum(payload) > 0
            else None
        ),
    )
    direct_sampling_value = _wait_for(
        "fresh Collector error keep decision",
        lambda: _collector_sampling_value(session, collector_metrics_url),
    )
    health_values = [float(item["value"][1]) for item in collector_health["data"]["result"]]

    for uid in ("prometheus", "tempo"):
        _wait_for(
            f"Grafana datasource {uid}",
            lambda uid=uid: _get_json(
                session,
                f"{grafana_base}/api/datasources/uid/{uid}",
                authorization=f"Basic {basic}",
            ),
        )
    dashboard = _wait_for(
        "provisioned dashboard",
        lambda: _get_json(
            session,
            f"{grafana_base}/api/dashboards/uid/agentic-operational-overview",
            authorization=f"Basic {basic}",
        ),
    )
    if dashboard["dashboard"]["editable"] is not False:
        raise SmokeError("provisioned dashboard must be read-only")

    print(
        json.dumps(
            {
                "dashboard_uid": dashboard["dashboard"]["uid"],
                "direct_sampling_value": direct_sampling_value,
                "error_metric_series": len(metric["data"]["result"]),
                "healthy_collector_targets": len(health_values),
                "prometheus_labels": sorted(labels),
                "sampling_series": len(sampling["data"]["result"]),
                "status": "pass",
                "trace_id": carrier.trace_id,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
