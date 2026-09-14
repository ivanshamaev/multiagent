"""Explicit content-free OpenTelemetry instrumentation for the control plane."""

from __future__ import annotations

import json
import os
import stat
import threading
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from pathlib import Path
from typing import Annotated, Any

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.trace import (
    NonRecordingSpan,
    Span,
    SpanContext,
    Status,
    StatusCode,
    TraceFlags,
    Tracer,
    TraceState,
)
from pydantic import StringConstraints, model_validator

from contracts import Artifact, ToolCallEvidence, ToolRequest, tool_arguments_sha256
from contracts.common import FrozenModel

MAX_TRACE_FILE_BYTES = 20_000_000
TRACE_SPAN_NAMES = frozenset(
    {
        "agentic.workflow",
        "agentic.role",
        "agentic.model",
        "agentic.tool",
        "agentic.artifact",
    }
)
COMMON_ATTRIBUTES = frozenset({"agentic.workflow.id", "agentic.task.id", "error.type"})
SPAN_ATTRIBUTES = {
    "agentic.workflow": COMMON_ATTRIBUTES
    | {
        "agentic.correlation.id",
        "agentic.workflow.stage",
        "agentic.workflow.revision",
    },
    "agentic.role": COMMON_ATTRIBUTES
    | {
        "agentic.role.name",
        "agentic.stage.input",
        "agentic.stage.output",
        "agentic.operation.id",
        "agentic.receipt.hit",
    },
    "agentic.model": {
        "agentic.model.schema",
        "agentic.model.request.sha256",
        "agentic.model.response.sha256",
        "agentic.model.latency_ms",
        "gen_ai.operation.name",
        "gen_ai.request.model",
        "gen_ai.response.finish_reasons",
        "gen_ai.usage.input_tokens",
        "gen_ai.usage.output_tokens",
        "error.type",
    },
    "agentic.tool": COMMON_ATTRIBUTES
    | {
        "agentic.tool.name",
        "agentic.tool.request.id",
        "agentic.tool.arguments.sha256",
        "agentic.tool.evidence.id",
        "agentic.tool.status",
        "agentic.tool.duration_ms",
        "agentic.tool.output_bytes",
    },
    "agentic.artifact": COMMON_ATTRIBUTES
    | {
        "agentic.artifact.id",
        "agentic.artifact.type",
        "agentic.artifact.producer.id",
        "agentic.event.hash",
    },
}

HexTraceId = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{32}$")]
HexSpanId = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{16}$")]


class TraceCarrier(FrozenModel):
    """Minimal W3C-compatible parent identity persisted in a typed checkpoint snapshot."""

    trace_id: HexTraceId
    workflow_span_id: HexSpanId

    @model_validator(mode="after")
    def reject_invalid_zero_ids(self):
        if int(self.trace_id, 16) == 0 or int(self.workflow_span_id, 16) == 0:
            raise ValueError("trace and span IDs must be non-zero")
        return self


class TelemetryError(RuntimeError):
    """Telemetry configuration or safe-export validation failed."""


class SafeSpan:
    """Expose only allowlisted attribute and sanitized error operations."""

    def __init__(self, span: Span, name: str) -> None:
        self._span = span
        self.name = name

    def set(self, key: str, value: str | int | bool) -> None:
        if key not in SPAN_ATTRIBUTES[self.name]:
            raise TelemetryError("telemetry attribute is not allowlisted")
        self._span.set_attribute(key, value)

    def fail(self, error: BaseException) -> None:
        self.set("error.type", type(error).__name__[:128])
        self._span.set_status(Status(StatusCode.ERROR))


def _carrier_context(carrier: TraceCarrier):
    parent = SpanContext(
        trace_id=int(carrier.trace_id, 16),
        span_id=int(carrier.workflow_span_id, 16),
        is_remote=True,
        trace_flags=TraceFlags(TraceFlags.SAMPLED),
        trace_state=TraceState(),
    )
    return trace.set_span_in_context(NonRecordingSpan(parent))


class AgenticTelemetry:
    """Typed façade for safe workflow, role, model, tool and artifact spans."""

    def __init__(self, provider: TracerProvider) -> None:
        self.provider = provider
        self.tracer: Tracer = provider.get_tracer("agentic-data-platform", "1.0")

    @contextmanager
    def workflow(
        self, *, workflow_id: str, task_id: str, correlation_id: str
    ) -> Iterator[tuple[SafeSpan, TraceCarrier]]:
        with self.tracer.start_as_current_span(
            "agentic.workflow", record_exception=False, set_status_on_exception=False
        ) as raw:
            span = SafeSpan(raw, "agentic.workflow")
            span.set("agentic.workflow.id", workflow_id)
            span.set("agentic.task.id", task_id)
            span.set("agentic.correlation.id", correlation_id)
            context = raw.get_span_context()
            carrier = TraceCarrier(
                trace_id=f"{context.trace_id:032x}",
                workflow_span_id=f"{context.span_id:016x}",
            )
            try:
                yield span, carrier
            except BaseException as error:
                span.fail(error)
                raise

    @contextmanager
    def role(
        self,
        carrier: TraceCarrier,
        *,
        workflow_id: str,
        task_id: str,
        role_name: str,
        input_stage: str,
        operation_id: str,
    ) -> Iterator[SafeSpan]:
        with self.tracer.start_as_current_span(
            "agentic.role",
            context=_carrier_context(carrier),
            record_exception=False,
            set_status_on_exception=False,
        ) as raw:
            span = SafeSpan(raw, "agentic.role")
            for key, value in {
                "agentic.workflow.id": workflow_id,
                "agentic.task.id": task_id,
                "agentic.role.name": role_name,
                "agentic.stage.input": input_stage,
                "agentic.operation.id": operation_id,
            }.items():
                span.set(key, value)
            try:
                yield span
            except BaseException as error:
                span.fail(error)
                raise

    @contextmanager
    def model(self, *, model_id: str, schema_name: str) -> Iterator[SafeSpan]:
        with self.tracer.start_as_current_span(
            "agentic.model", record_exception=False, set_status_on_exception=False
        ) as raw:
            span = SafeSpan(raw, "agentic.model")
            span.set("gen_ai.operation.name", "chat")
            span.set("gen_ai.request.model", model_id)
            span.set("agentic.model.schema", schema_name)
            try:
                yield span
            except BaseException as error:
                span.fail(error)
                raise

    @contextmanager
    def tool(self, request: ToolRequest) -> Iterator[SafeSpan]:
        with self.tracer.start_as_current_span(
            "agentic.tool", record_exception=False, set_status_on_exception=False
        ) as raw:
            span = SafeSpan(raw, "agentic.tool")
            span.set("agentic.task.id", request.task_id)
            span.set("agentic.tool.name", request.call.tool.value)
            span.set("agentic.tool.request.id", request.request_id)
            span.set("agentic.tool.arguments.sha256", tool_arguments_sha256(request.call))
            try:
                yield span
            except BaseException as error:
                span.fail(error)
                raise

    def complete_model(self, span: SafeSpan, invocation: Any) -> None:
        span.set("gen_ai.usage.input_tokens", invocation.usage.input_tokens)
        span.set("gen_ai.usage.output_tokens", invocation.usage.output_tokens)
        span.set("agentic.model.latency_ms", invocation.latency_ms)
        span.set("agentic.model.request.sha256", invocation.request_sha256)
        span.set("agentic.model.response.sha256", invocation.response_sha256)
        if invocation.finish_reason is not None:
            span.set("gen_ai.response.finish_reasons", invocation.finish_reason)

    def complete_tool(self, span: SafeSpan, evidence: ToolCallEvidence) -> None:
        span.set("agentic.tool.evidence.id", evidence.evidence_id)
        span.set("agentic.tool.status", evidence.status.value)
        span.set("agentic.tool.duration_ms", evidence.duration_ms)
        span.set("agentic.tool.output_bytes", evidence.output_bytes)

    def artifact(
        self,
        artifact: Artifact,
        *,
        workflow_id: str,
        event_hash: str,
    ) -> None:
        with self.tracer.start_as_current_span(
            "agentic.artifact", record_exception=False, set_status_on_exception=False
        ) as raw:
            span = SafeSpan(raw, "agentic.artifact")
            for key, value in {
                "agentic.workflow.id": workflow_id,
                "agentic.task.id": artifact.task_id,
                "agentic.artifact.id": artifact.artifact_id,
                "agentic.artifact.type": artifact.artifact_type,
                "agentic.artifact.producer.id": artifact.producer_id,
                "agentic.event.hash": event_hash,
            }.items():
                span.set(key, value)

    def shutdown(self) -> None:
        self.provider.shutdown()


def build_telemetry(exporter: SpanExporter) -> AgenticTelemetry:
    provider = TracerProvider(resource=Resource.create({"service.name": "agentic-data-platform"}))
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    return AgenticTelemetry(provider)


class SanitizedJsonSpanExporter(SpanExporter):
    """Append only the closed, content-free span schema to a local owner-only JSONL file."""

    def __init__(self, repository_root: Path, output_path: Path) -> None:
        if repository_root.is_symlink():
            raise TelemetryError("repository root must not be a symlink")
        root = repository_root.resolve(strict=True)
        if not output_path.is_absolute():
            raise TelemetryError("trace output path must be absolute")
        try:
            relative = output_path.relative_to(root)
        except ValueError:
            raise TelemetryError("trace output escaped the repository") from None
        current = root
        for component in relative.parts:
            current /= component
            if current.is_symlink():
                raise TelemetryError("trace output path must not contain symlinks")
        resolved = output_path.resolve(strict=False)
        if not resolved.is_relative_to(root):
            raise TelemetryError("trace output escaped the repository")
        resolved.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if stat.S_IMODE(resolved.parent.stat().st_mode) != 0o700:
            raise TelemetryError("trace output directory must have mode 0700")
        if resolved.exists():
            metadata = resolved.lstat()
            if resolved.is_symlink() or not stat.S_ISREG(metadata.st_mode):
                raise TelemetryError("trace output must be a regular non-symlink file")
            if stat.S_IMODE(metadata.st_mode) != 0o600:
                raise TelemetryError("trace output must have mode 0600")
            if metadata.st_size > MAX_TRACE_FILE_BYTES:
                raise TelemetryError("trace output exceeds the size limit")
        self.output_path = resolved
        self._lock = threading.Lock()

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        lines = tuple(self._encode(item) for item in spans)
        with self._lock:
            existing_size = self.output_path.stat().st_size if self.output_path.exists() else 0
            payload = b"".join(lines)
            if existing_size + len(payload) > MAX_TRACE_FILE_BYTES:
                raise TelemetryError("trace output exceeds the size limit")
            descriptor = os.open(
                self.output_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW, 0o600
            )
            try:
                with os.fdopen(descriptor, "ab") as stream:
                    stream.write(payload)
                    stream.flush()
                    os.fsync(stream.fileno())
            finally:
                if self.output_path.exists():
                    self.output_path.chmod(0o600)
        return SpanExportResult.SUCCESS

    @staticmethod
    def _encode(span: ReadableSpan) -> bytes:
        if span.name not in TRACE_SPAN_NAMES:
            raise TelemetryError("trace contains an unknown span name")
        attributes = dict(span.attributes or {})
        if not attributes.keys() <= SPAN_ATTRIBUTES[span.name]:
            raise TelemetryError("trace contains a non-allowlisted attribute")
        context = span.context
        if context is None:
            raise TelemetryError("trace span has no context")
        parent_span_id = None if span.parent is None else f"{span.parent.span_id:016x}"
        payload = {
            "attributes": attributes,
            "end_time_unix_nano": span.end_time,
            "name": span.name,
            "parent_span_id": parent_span_id,
            "span_id": f"{context.span_id:016x}",
            "start_time_unix_nano": span.start_time,
            "status": span.status.status_code.name,
            "trace_id": f"{context.trace_id:032x}",
        }
        return (
            json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"
        ).encode("utf-8")
