import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

EXPECTED_IMAGES = {
    "otel/opentelemetry-collector-contrib:0.160.0@sha256:799dc6cf12c96192af37b5bdba804da8c10b3bc563b43cb90c3f3c58d9572ad6",
    "grafana/tempo:3.0.3@sha256:0296560ac66f8a3600d7fb3014a52c189d4d9c3549ad6ff441bf2409855d68d5",
    "prom/prometheus:v3.14.0@sha256:5ce7540c3c00ef4ab0c9d2c995c6a5b9c421f44b4a115d97a2c7af3b1c21cbb0",
    "grafana/grafana:13.2.1@sha256:f772d434e8fab0049deb2b1b30abd43342bcfca1537614aa8d36080232cf4283",
}


def test_observability_images_ports_network_and_retention_are_bounded() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert all(image in compose for image in EXPECTED_IMAGES)
    for port in (
        "OTEL_HTTP_PORT",
        "OTEL_METRICS_PORT",
        "TEMPO_HTTP_PORT",
        "PROMETHEUS_HTTP_PORT",
        "GRAFANA_HTTP_PORT",
    ):
        assert f'"127.0.0.1:${{{port}' in compose
    assert "--storage.tsdb.retention.time=7d" in compose
    assert "--storage.tsdb.retention.size=1GB" in compose
    assert "  observability:\n    driver: bridge\n    internal: true" in compose
    for service in ("otel", "tempo", "prometheus", "grafana"):
        assert f"  observability-{service}-host:\n    driver: bridge" in compose
    assert "docker.sock" not in compose

    tempo = (ROOT / "observability/tempo.yaml").read_text(encoding="utf-8")
    assert tempo.count("block_retention: 72h") == 2
    assert "backend_scheduler:" in tempo
    assert "backend_worker:" in tempo
    assert "\ningester:" not in tempo
    assert "\ncompactor:" not in tempo
    assert "backend: local" in tempo


def test_collector_sampling_metrics_and_cardinality_policy_are_explicit() -> None:
    collector = (ROOT / "observability/otel-collector.yaml").read_text(encoding="utf-8")
    assert "status_codes: [ERROR]" in collector
    assert "sampling_percentage: 25" in collector
    assert "memory_limiter:" in collector
    assert "span_metrics:" in collector
    for allowed in (
        "agentic.role.name",
        "gen_ai.request.model",
        "agentic.tool.name",
        "agentic.workflow.stage",
        "agentic.receipt.hit",
    ):
        assert f"- name: {allowed}" in collector
    for forbidden in (
        "agentic.workflow.id",
        "agentic.task.id",
        "agentic.operation.id",
        "agentic.tool.request.id",
        "agentic.artifact.id",
    ):
        assert f"- name: {forbidden}" not in collector


def test_dashboard_is_provisioned_read_only_with_operational_panels() -> None:
    dashboard = json.loads(
        (ROOT / "observability/grafana/dashboards/agentic-overview.json").read_text(
            encoding="utf-8"
        )
    )
    assert dashboard["uid"] == "agentic-operational-overview"
    assert dashboard["editable"] is False
    titles = {panel["title"] for panel in dashboard["panels"]}
    assert titles == {
        "Sampled span throughput",
        "Error throughput",
        "p95 span latency",
        "Role, model and tool totals",
        "Workflow stage and receipt replay",
        "Tail sampling decisions",
    }
    sampling_panel = next(
        panel for panel in dashboard["panels"] if panel["title"] == "Tail sampling decisions"
    )
    assert (
        "otelcol_processor_tail_sampling_count_traces_sampled{"
        in sampling_panel["targets"][0]["expr"]
    )
    assert 'sampled="true"' in sampling_panel["targets"][0]["expr"]
    provisioning = (
        ROOT / "observability/grafana/provisioning/dashboards/dashboards.yaml"
    ).read_text(encoding="utf-8")
    assert "allowUiUpdates: false" in provisioning
    assert "disableDeletion: true" in provisioning
