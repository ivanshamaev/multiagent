"""Bounded GET-only adapter for the pinned Airflow public API."""

from __future__ import annotations

import json
import math
import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from contracts import (
    AirflowGetDagCall,
    AirflowGetDagRunCall,
    AirflowGetTaskLogCall,
    AirflowListDagRunsCall,
    AirflowListDagsCall,
    AirflowListTaskInstancesCall,
)

AirflowCall = (
    AirflowListDagsCall
    | AirflowGetDagCall
    | AirflowListDagRunsCall
    | AirflowGetDagRunCall
    | AirflowListTaskInstancesCall
    | AirflowGetTaskLogCall
)
DAG_FIELDS = frozenset(
    {
        "dag_id",
        "dag_display_name",
        "description",
        "has_import_errors",
        "is_paused",
        "is_stale",
        "last_parsed_time",
        "owners",
        "tags",
        "timetable_description",
        "timetable_summary",
    }
)
RUN_FIELDS = frozenset(
    {
        "dag_id",
        "dag_run_id",
        "data_interval_end",
        "data_interval_start",
        "duration",
        "end_date",
        "logical_date",
        "run_after",
        "run_type",
        "start_date",
        "state",
    }
)
TASK_INSTANCE_FIELDS = frozenset(
    {
        "dag_id",
        "dag_run_id",
        "duration",
        "end_date",
        "map_index",
        "operator",
        "start_date",
        "state",
        "task_id",
        "try_number",
    }
)


class AirflowAPIError(RuntimeError):
    """A safely reportable Airflow API boundary failure."""


class AirflowTransport(Protocol):
    def __call__(self, request: Request, timeout: float, max_bytes: int) -> tuple[int, bytes]: ...


class _NoRedirects(HTTPRedirectHandler):
    def redirect_request(
        self,
        req: Request,
        fp: object,
        code: int,
        msg: str,
        headers: object,
        newurl: str,
    ) -> None:
        return None


def _stdlib_transport(request: Request, timeout: float, max_bytes: int) -> tuple[int, bytes]:
    try:
        with build_opener(_NoRedirects()).open(request, timeout=timeout) as response:
            return response.status, response.read(max_bytes + 1)
    except HTTPError as error:
        try:
            return error.code, error.read(max_bytes + 1)
        finally:
            error.close()


def _required(environ: Mapping[str, str], name: str) -> str:
    value = environ.get(name, "").strip()
    if not value:
        raise AirflowAPIError(f"required environment variable {name} is missing")
    return value


@dataclass(frozen=True, slots=True)
class AirflowAPIConfig:
    base_url: str
    username: str = field(repr=False)
    password: str = field(repr=False)
    allowed_dags: frozenset[str]
    timeout_seconds: float = 10.0
    max_response_bytes: int = 250_000

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> AirflowAPIConfig:
        values = os.environ if environ is None else environ
        base_url = _required(values, "AIRFLOW_API_BASE_URL").rstrip("/")
        parsed = urlsplit(base_url)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.netloc
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            raise AirflowAPIError("AIRFLOW_API_BASE_URL must be an absolute credential-free URL")
        if parsed.scheme == "http" and parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
            raise AirflowAPIError("Airflow MCP requires HTTPS outside loopback")
        dags = frozenset(
            item.strip()
            for item in _required(values, "AIRFLOW_MCP_ALLOWED_DAGS").split(",")
            if item.strip()
        )
        if not dags:
            raise AirflowAPIError("AIRFLOW_MCP_ALLOWED_DAGS must not be empty")
        try:
            timeout = float(values.get("AIRFLOW_API_REQUEST_TIMEOUT_SECONDS", "10"))
            max_bytes = int(values.get("AIRFLOW_MCP_MAX_RESPONSE_BYTES", "250000"))
        except ValueError:
            raise AirflowAPIError("Airflow MCP numeric configuration is invalid") from None
        if not math.isfinite(timeout) or timeout <= 0 or not 1 <= max_bytes <= 1_000_000:
            raise AirflowAPIError("Airflow MCP numeric configuration is outside bounds")
        return cls(
            base_url=base_url,
            username=_required(values, "AIRFLOW_MCP_USERNAME"),
            password=_required(values, "AIRFLOW_MCP_PASSWORD"),
            allowed_dags=dags,
            timeout_seconds=timeout,
            max_response_bytes=max_bytes,
        )


class AirflowAPIAdapter:
    """Translate closed tool contracts into fixed Airflow GET requests."""

    def __init__(
        self,
        config: AirflowAPIConfig,
        *,
        transport: AirflowTransport = _stdlib_transport,
    ) -> None:
        self._config = config
        self._transport = transport
        self._token: str | None = None

    def execute(self, call: AirflowCall) -> str:
        if isinstance(call, AirflowListDagsCall):
            payload = self._get_json("/api/v2/dags", {"limit": 100, "offset": 0})
            body = self._object(payload, "DAG list")
            dags = body.get("dags")
            if not isinstance(dags, list):
                raise AirflowAPIError("Airflow DAG list response is invalid")
            allowed = [
                self._project(item, DAG_FIELDS, "dag_id", "DAG list")
                for item in dags
                if isinstance(item, dict) and item.get("dag_id") in self._config.allowed_dags
            ]
            selected = allowed[call.offset : call.offset + call.limit]
            return self._canonical({"dags": selected, "total_entries": len(allowed)})

        self._require_allowed(call.dag_id)
        dag = quote(call.dag_id, safe="")
        if isinstance(call, AirflowGetDagCall):
            payload = self._project(
                self._object(self._get_json(f"/api/v2/dags/{dag}"), "DAG"),
                DAG_FIELDS,
                "dag_id",
                "DAG",
            )
        elif isinstance(call, AirflowListDagRunsCall):
            payload = self._project_collection(
                self._get_json(
                    f"/api/v2/dags/{dag}/dagRuns",
                    {"limit": call.limit, "offset": call.offset, "order_by": "-id"},
                ),
                "dag_runs",
                RUN_FIELDS,
                "dag_run_id",
            )
        else:
            run = quote(call.dag_run_id, safe="")
            run_path = f"/api/v2/dags/{dag}/dagRuns/{run}"
            if isinstance(call, AirflowGetDagRunCall):
                payload = self._project(
                    self._object(self._get_json(run_path), "DAG run"),
                    RUN_FIELDS,
                    "dag_run_id",
                    "DAG run",
                )
            elif isinstance(call, AirflowListTaskInstancesCall):
                payload = self._project_collection(
                    self._get_json(
                        f"{run_path}/taskInstances",
                        {"limit": call.limit, "offset": call.offset},
                    ),
                    "task_instances",
                    TASK_INSTANCE_FIELDS,
                    "task_id",
                )
            else:
                task = quote(call.task_id, safe="")
                payload = self._get_json(
                    f"{run_path}/taskInstances/{task}/logs/{call.try_number}",
                    {"full_content": "false", "map_index": call.map_index},
                )
        return self._canonical(payload)

    def _require_allowed(self, dag_id: str) -> None:
        if dag_id not in self._config.allowed_dags:
            raise AirflowAPIError("Airflow DAG is not allowed")

    def _authenticate(self) -> str:
        request = Request(
            f"{self._config.base_url}/auth/token",
            data=json.dumps(
                {"username": self._config.username, "password": self._config.password},
                separators=(",", ":"),
            ).encode(),
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            method="POST",
        )
        status, body = self._send(request)
        if status != 201:
            raise AirflowAPIError(f"Airflow authentication returned HTTP {status}")
        payload = self._decode_json(body, "authentication")
        token = self._object(payload, "authentication").get("access_token")
        if not isinstance(token, str) or not token:
            raise AirflowAPIError("Airflow authentication response is invalid")
        self._token = token
        return token

    def _get_json(self, path: str, query: Mapping[str, object] | None = None) -> object:
        if not path.startswith("/api/v2/") or "?" in path or "#" in path:
            raise AirflowAPIError("Airflow adapter constructed an unsafe API path")
        suffix = "" if not query else f"?{urlencode(query)}"
        token = self._token or self._authenticate()
        request = Request(
            f"{self._config.base_url}{path}{suffix}",
            headers={"Accept": "application/json", "Authorization": f"Bearer {token}"},
            method="GET",
        )
        status, body = self._send(request)
        if status != 200:
            raise AirflowAPIError(f"Airflow GET returned HTTP {status}")
        return self._decode_json(body, "GET")

    def _send(self, request: Request) -> tuple[int, bytes]:
        try:
            status, body = self._transport(
                request,
                self._config.timeout_seconds,
                self._config.max_response_bytes,
            )
        except (TimeoutError, URLError, OSError) as error:
            raise AirflowAPIError(f"Airflow request failed ({type(error).__name__})") from None
        if len(body) > self._config.max_response_bytes:
            raise AirflowAPIError("Airflow response exceeded the byte limit")
        return status, body

    @staticmethod
    def _decode_json(body: bytes, operation: str) -> object:
        try:
            return json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise AirflowAPIError(f"Airflow {operation} response is invalid JSON") from None

    @staticmethod
    def _object(payload: object, operation: str) -> dict[str, object]:
        if not isinstance(payload, dict):
            raise AirflowAPIError(f"Airflow {operation} response is invalid")
        return payload

    @classmethod
    def _project_collection(
        cls,
        payload: object,
        key: str,
        fields: frozenset[str],
        identity_field: str,
    ) -> dict[str, object]:
        body = cls._object(payload, key)
        items = body.get(key)
        if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
            raise AirflowAPIError(f"Airflow {key} response is invalid")
        result: dict[str, object] = {
            key: [cls._project(item, fields, identity_field, key) for item in items]
        }
        if isinstance(body.get("total_entries"), int):
            result["total_entries"] = body["total_entries"]
        return result

    @staticmethod
    def _project(
        payload: dict[str, object],
        fields: frozenset[str],
        identity_field: str,
        operation: str,
    ) -> dict[str, object]:
        if not isinstance(payload.get(identity_field), str):
            raise AirflowAPIError(f"Airflow {operation} response is missing identity")
        return {key: payload[key] for key in sorted(fields) if key in payload}

    @staticmethod
    def _canonical(payload: object) -> str:
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
