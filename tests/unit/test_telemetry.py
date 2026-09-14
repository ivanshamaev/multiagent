import json
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from pydantic import ValidationError

from contracts import (
    ArtifactReference,
    ToolCallEvidence,
    ToolCallStatus,
    ToolRequest,
    tool_arguments_sha256,
)
from runtime.model_provider import ModelCallRecord, ModelUsage
from runtime.telemetry import (
    AgenticTelemetry,
    SanitizedJsonSpanExporter,
    TelemetryError,
    TraceCarrier,
    build_telemetry,
)
from tests.workflow.factories import task_request


def _memory_telemetry() -> tuple[AgenticTelemetry, InMemorySpanExporter]:
    exporter = InMemorySpanExporter()
    return build_telemetry(exporter), exporter


def test_safe_facade_builds_one_content_free_trace_hierarchy() -> None:
    telemetry, exporter = _memory_telemetry()
    model_call = ModelCallRecord(
        model_id="fake/cheap-model",
        usage=ModelUsage(input_tokens=10, output_tokens=5, total_tokens=15),
        latency_ms=12,
        finish_reason="stop",
        request_sha256="a" * 64,
        response_sha256="b" * 64,
    )
    artifact = task_request()
    tool_request = ToolRequest(
        request_id="request-1",
        task_id=artifact.task_id,
        actor_id="data-engineer-1",
        role="data-engineer",
        call={"tool": "dbt.parse"},
    )
    tool_output = b"{}"
    tool_evidence = ToolCallEvidence(
        evidence_id="evidence-1",
        request_id=tool_request.request_id,
        task_id=tool_request.task_id,
        producer_id="mcp-gateway",
        tool=tool_request.call.tool,
        arguments_sha256=tool_arguments_sha256(tool_request.call),
        started_at=datetime(2026, 9, 14, tzinfo=UTC),
        completed_at=datetime(2026, 9, 14, tzinfo=UTC),
        status=ToolCallStatus.SUCCESS,
        exit_code=0,
        duration_ms=7,
        output_bytes=len(tool_output),
        output=ArtifactReference(
            path=".evidence/tool.json",
            sha256=sha256(tool_output).hexdigest(),
            media_type="application/json",
            size_bytes=len(tool_output),
        ),
    )

    with telemetry.workflow(
        workflow_id="workflow-1", task_id=artifact.task_id, correlation_id="correlation-1"
    ) as (workflow_span, carrier):
        with telemetry.role(
            carrier,
            workflow_id="workflow-1",
            task_id=artifact.task_id,
            role_name="analyst",
            input_stage="unstarted",
            operation_id="operation-1",
        ) as role_span:
            with telemetry.model(model_id="fake/cheap-model", schema_name="TaskRequest") as span:
                telemetry.complete_model(span, model_call)
            with telemetry.tool(tool_request) as span:
                telemetry.complete_tool(span, tool_evidence)
            telemetry.artifact(artifact, workflow_id="workflow-1", event_hash="c" * 64)
            role_span.set("agentic.stage.output", "analysis_ready")
            role_span.set("agentic.receipt.hit", False)
        workflow_span.set("agentic.workflow.stage", "analysis_ready")
        workflow_span.set("agentic.workflow.revision", 2)

    spans = {span.name: span for span in exporter.get_finished_spans()}
    workflow = spans["agentic.workflow"]
    role = spans["agentic.role"]
    model = spans["agentic.model"]
    tool = spans["agentic.tool"]
    accepted_artifact = spans["agentic.artifact"]

    assert {span.context.trace_id for span in spans.values()} == {int(carrier.trace_id, 16)}
    assert workflow.parent is None
    assert role.parent.span_id == workflow.context.span_id
    assert model.parent.span_id == role.context.span_id
    assert tool.parent.span_id == role.context.span_id
    assert accepted_artifact.parent.span_id == role.context.span_id
    assert model.attributes["agentic.model.request.sha256"] == "a" * 64
    assert tool.attributes["agentic.tool.status"] == "success"
    assert accepted_artifact.attributes["agentic.event.hash"] == "c" * 64
    assert "description" not in json.dumps(
        [dict(span.attributes or {}) for span in spans.values()], sort_keys=True
    )


def test_error_span_records_only_exception_type() -> None:
    telemetry, exporter = _memory_telemetry()
    secret = "API_TOKEN=must-never-be-exported"

    with pytest.raises(RuntimeError, match="must-never"):
        with telemetry.workflow(
            workflow_id="workflow-1", task_id="task-1", correlation_id="correlation-1"
        ) as (_, carrier):
            with telemetry.role(
                carrier,
                workflow_id="workflow-1",
                task_id="task-1",
                role_name="pm",
                input_stage="analysis_ready",
                operation_id="operation-1",
            ):
                raise RuntimeError(secret)

    spans = exporter.get_finished_spans()
    assert all(span.status.status_code.name == "ERROR" for span in spans)
    assert all(span.attributes["error.type"] == "RuntimeError" for span in spans)
    assert all(not span.events for span in spans)
    assert secret not in repr(
        [(dict(span.attributes or {}), span.status.description, span.events) for span in spans]
    )


def test_trace_carrier_and_attribute_allowlist_fail_closed() -> None:
    with pytest.raises(ValidationError, match="non-zero"):
        TraceCarrier(trace_id="0" * 32, workflow_span_id="0" * 16)

    telemetry, _ = _memory_telemetry()
    with telemetry.workflow(
        workflow_id="workflow-1", task_id="task-1", correlation_id="correlation-1"
    ) as (span, _):
        with pytest.raises(TelemetryError, match="allowlisted"):
            span.set("prompt", "unsafe")


def test_sanitized_json_exporter_writes_closed_owner_only_jsonl(tmp_path: Path) -> None:
    output_path = tmp_path / "traces" / "spans.jsonl"
    telemetry = build_telemetry(SanitizedJsonSpanExporter(tmp_path, output_path))

    with telemetry.workflow(
        workflow_id="workflow-1", task_id="task-1", correlation_id="correlation-1"
    ) as (span, _):
        span.set("agentic.workflow.stage", "done")
        span.set("agentic.workflow.revision", 12)
    telemetry.shutdown()

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["name"] == "agentic.workflow"
    assert payload["attributes"]["agentic.workflow.stage"] == "done"
    assert output_path.parent.stat().st_mode & 0o777 == 0o700
    assert output_path.stat().st_mode & 0o777 == 0o600
    assert set(payload) == {
        "attributes",
        "end_time_unix_nano",
        "name",
        "parent_span_id",
        "span_id",
        "start_time_unix_nano",
        "status",
        "trace_id",
    }


def test_sanitized_exporter_rejects_unknown_raw_span_attribute(tmp_path: Path) -> None:
    memory = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(memory))
    with provider.get_tracer("unsafe-test").start_as_current_span("agentic.workflow") as span:
        span.set_attribute("prompt", "unsafe payload")
    readable = memory.get_finished_spans()[0]

    with pytest.raises(TelemetryError, match="non-allowlisted"):
        SanitizedJsonSpanExporter._encode(readable)
