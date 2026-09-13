"""Approved, idempotent adapter for one fixed Airflow DAG-run POST."""

from __future__ import annotations

import json
import math
import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from contracts import AirflowTriggerDagCall
from runtime.tools.airflow_api import RUN_FIELDS
from runtime.tools.airflow_approval import AirflowApprovalError, AirflowApprovalStore


class AirflowTriggerError(RuntimeError):
    """A safely reportable trigger-boundary failure."""


class AirflowTriggerTransport(Protocol):
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


def _transport(request: Request, timeout: float, max_bytes: int) -> tuple[int, bytes]:
    try:
        with build_opener(_NoRedirects()).open(request, timeout=timeout) as response:
            return response.status, response.read(max_bytes + 1)
    except HTTPError as error:
        try:
            return error.code, error.read(max_bytes + 1)
        finally:
            error.close()


def _required(values: Mapping[str, str], name: str) -> str:
    value = values.get(name, "").strip()
    if not value:
        raise AirflowTriggerError(f"required environment variable {name} is missing")
    return value


@dataclass(frozen=True, slots=True)
class AirflowTriggerConfig:
    repository_root: Path
    base_url: str
    username: str = field(repr=False)
    password: str = field(repr=False)
    allowed_dag: str = "ecommerce_acceptance"
    approval_root: Path | None = None
    timeout_seconds: float = 10.0
    max_response_bytes: int = 50_000

    @classmethod
    def from_env(cls, values: Mapping[str, str] | None = None) -> AirflowTriggerConfig:
        environ = os.environ if values is None else values
        base_url = _required(environ, "AIRFLOW_API_BASE_URL").rstrip("/")
        parsed = urlsplit(base_url)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.netloc
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            raise AirflowTriggerError("AIRFLOW_API_BASE_URL must be credential-free")
        if parsed.scheme == "http" and parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
            raise AirflowTriggerError("Airflow trigger requires HTTPS outside loopback")
        try:
            timeout = float(environ.get("AIRFLOW_API_REQUEST_TIMEOUT_SECONDS", "10"))
            max_bytes = int(environ.get("AIRFLOW_TRIGGER_MAX_RESPONSE_BYTES", "50000"))
        except ValueError:
            raise AirflowTriggerError("Airflow trigger numeric configuration is invalid") from None
        if not math.isfinite(timeout) or timeout <= 0 or not 1 <= max_bytes <= 100_000:
            raise AirflowTriggerError("Airflow trigger numeric configuration is outside bounds")
        repository = Path(_required(environ, "AIRFLOW_TRIGGER_REPOSITORY_ROOT"))
        approval_root = Path(_required(environ, "AIRFLOW_TRIGGER_APPROVAL_ROOT"))
        return cls(
            repository_root=repository,
            base_url=base_url,
            username=_required(environ, "AIRFLOW_TRIGGER_USERNAME"),
            password=_required(environ, "AIRFLOW_TRIGGER_PASSWORD"),
            allowed_dag=_required(environ, "AIRFLOW_TRIGGER_ALLOWED_DAG"),
            approval_root=approval_root,
            timeout_seconds=timeout,
            max_response_bytes=max_bytes,
        )


class AirflowTriggerAdapter:
    """Validate approval and reconcile a deterministic run ID around one POST."""

    def __init__(
        self,
        config: AirflowTriggerConfig,
        *,
        transport: AirflowTriggerTransport = _transport,
        approvals: AirflowApprovalStore | None = None,
    ) -> None:
        self._config = config
        self._transport = transport
        self._approvals = approvals or AirflowApprovalStore(
            config.repository_root,
            config.approval_root,
        )
        self._token: str | None = None

    def execute(self, call: AirflowTriggerDagCall) -> str:
        if call.dag_id != self._config.allowed_dag:
            raise AirflowTriggerError("Airflow DAG is not allowed for controlled trigger")
        run_id = self.run_id(call.dag_id, call.idempotency_key)
        try:
            claim_context = self._approvals.claim(
                approval_id=call.approval_id,
                task_id=call.task_id,
                dag_id=call.dag_id,
                idempotency_key=call.idempotency_key,
            )
            with claim_context as claim:
                existing = self._lookup(call.dag_id, run_id)
                created = False
                if existing is None:
                    existing, created = self._create(call.dag_id, run_id)
                claim.consume(run_id)
        except AirflowApprovalError as error:
            raise AirflowTriggerError(str(error)) from None
        result = dict(existing)
        result["trigger_outcome"] = "created" if created else "existing"
        return json.dumps(result, ensure_ascii=False, separators=(",", ":"), sort_keys=True)

    @staticmethod
    def run_id(dag_id: str, idempotency_key: str) -> str:
        digest = sha256(f"{dag_id}:{idempotency_key}".encode()).hexdigest()[:32]
        return f"approved__{digest}"

    def _lookup(self, dag_id: str, run_id: str) -> dict[str, object] | None:
        dag = quote(dag_id, safe="")
        run = quote(run_id, safe="")
        status, body = self._request("GET", f"/api/v2/dags/{dag}/dagRuns/{run}")
        if status == 404:
            return None
        if status != 200:
            raise AirflowTriggerError(f"Airflow trigger reconciliation returned HTTP {status}")
        return self._project(body, dag_id, run_id)

    def _create(self, dag_id: str, run_id: str) -> tuple[dict[str, object], bool]:
        dag = quote(dag_id, safe="")
        body = json.dumps(
            {"conf": {}, "dag_run_id": run_id, "logical_date": None},
            separators=(",", ":"),
        ).encode()
        try:
            status, response = self._request(
                "POST",
                f"/api/v2/dags/{dag}/dagRuns",
                body=body,
            )
        except AirflowTriggerError:
            reconciled = self._lookup(dag_id, run_id)
            if reconciled is not None:
                return reconciled, True
            raise
        if status == 200:
            return self._project(response, dag_id, run_id), True
        if status == 409:
            reconciled = self._lookup(dag_id, run_id)
            if reconciled is not None:
                return reconciled, False
        raise AirflowTriggerError(f"Airflow trigger returned HTTP {status}")

    def _authenticate(self) -> str:
        body = json.dumps(
            {"username": self._config.username, "password": self._config.password},
            separators=(",", ":"),
        ).encode()
        status, response = self._request("POST", "/auth/token", body=body, authenticated=False)
        if status != 201:
            raise AirflowTriggerError(f"Airflow trigger authentication returned HTTP {status}")
        payload = self._decode(response)
        token = payload.get("access_token")
        if not isinstance(token, str) or not token:
            raise AirflowTriggerError("Airflow trigger authentication response is invalid")
        self._token = token
        return token

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: bytes | None = None,
        authenticated: bool = True,
    ) -> tuple[int, bytes]:
        if not (path == "/auth/token" or path.startswith("/api/v2/dags/")) or any(
            marker in path for marker in ("?", "#")
        ):
            raise AirflowTriggerError("Airflow trigger constructed an unsafe path")
        headers = {"Accept": "application/json"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        if authenticated:
            headers["Authorization"] = f"Bearer {self._token or self._authenticate()}"
        request = Request(
            f"{self._config.base_url}{path}",
            data=body,
            headers=headers,
            method=method,
        )
        try:
            status, response = self._transport(
                request,
                self._config.timeout_seconds,
                self._config.max_response_bytes,
            )
        except (TimeoutError, URLError, OSError) as error:
            raise AirflowTriggerError(
                f"Airflow trigger request failed ({type(error).__name__})"
            ) from None
        if len(response) > self._config.max_response_bytes:
            raise AirflowTriggerError("Airflow trigger response exceeded the byte limit")
        return status, response

    def _project(self, body: bytes, dag_id: str, run_id: str) -> dict[str, object]:
        payload = self._decode(body)
        if payload.get("dag_id") != dag_id or payload.get("dag_run_id") != run_id:
            raise AirflowTriggerError("Airflow trigger response identity is invalid")
        return {key: payload[key] for key in sorted(RUN_FIELDS) if key in payload}

    @staticmethod
    def _decode(body: bytes) -> dict[str, object]:
        try:
            payload = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise AirflowTriggerError("Airflow trigger response is invalid JSON") from None
        if not isinstance(payload, dict):
            raise AirflowTriggerError("Airflow trigger response is invalid")
        return payload
