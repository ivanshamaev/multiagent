import asyncio
from pathlib import Path

from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from orchestrator import Stage
from runtime.checkpoints import SecureCheckpointStorage
from runtime.role_pipeline import (
    AnalystExecutor,
    build_role_pipeline,
    decode_role_snapshot,
    initial_role_message,
    run_traced_role_pipeline,
)
from runtime.role_receipts import SecureRoleReceiptStore
from runtime.telemetry import build_telemetry
from tests.workflow.test_role_pipeline import _handlers, _request


def test_role_pipeline_exports_one_workflow_role_artifact_trace(tmp_path: Path) -> None:
    calls: list[str] = []
    exporter = InMemorySpanExporter()
    telemetry = build_telemetry(exporter)
    storage = SecureCheckpointStorage(tmp_path, tmp_path / "checkpoints")
    receipts = SecureRoleReceiptStore(tmp_path, tmp_path / "receipts")
    workflow = build_role_pipeline(_handlers(calls), storage, receipts, telemetry=telemetry)

    result = asyncio.run(run_traced_role_pipeline(workflow, _request(), telemetry))
    snapshot = decode_role_snapshot(result.get_outputs()[0])
    spans = exporter.get_finished_spans()
    workflow_span = next(span for span in spans if span.name == "agentic.workflow")
    role_spans = [span for span in spans if span.name == "agentic.role"]
    artifact_spans = [span for span in spans if span.name == "agentic.artifact"]

    assert snapshot.state is not None and snapshot.state.stage is Stage.DONE
    assert snapshot.trace is not None
    assert snapshot.trace.trace_id == f"{workflow_span.context.trace_id:032x}"
    assert len(role_spans) == 6
    assert len(artifact_spans) == 6
    assert len({span.context.trace_id for span in spans}) == 1
    assert all(span.parent.span_id == workflow_span.context.span_id for span in role_spans)
    role_ids = {span.context.span_id for span in role_spans}
    assert all(span.parent.span_id in role_ids for span in artifact_spans)
    assert [span.attributes["agentic.role.name"] for span in role_spans] == calls
    assert all(span.attributes["agentic.receipt.hit"] is False for span in role_spans)
    assert workflow_span.attributes["agentic.workflow.stage"] == "done"
    assert workflow_span.attributes["agentic.workflow.revision"] == 12


def test_receipt_retry_is_traced_without_reemitting_artifact(tmp_path: Path) -> None:
    calls: list[str] = []
    exporter = InMemorySpanExporter()
    telemetry = build_telemetry(exporter)
    receipts = SecureRoleReceiptStore(tmp_path, tmp_path / "receipts")
    executor = AnalystExecutor(
        "role_analyst",
        _handlers(calls).analyst,
        frozenset({None}),
        frozenset({Stage.ANALYSIS_READY}),
        receipt_store=receipts,
        telemetry=telemetry,
    )

    with telemetry.workflow(
        workflow_id=_request().workflow_id,
        task_id=_request().task.task_id,
        correlation_id=_request().correlation_id,
    ) as (_, carrier):
        payload = initial_role_message(_request(), trace_carrier=carrier)
        first = asyncio.run(executor.advance(payload))
        second = asyncio.run(executor.advance(payload))

    assert first == second
    assert calls == ["analyst"]
    role_spans = [span for span in exporter.get_finished_spans() if span.name == "agentic.role"]
    artifact_spans = [
        span for span in exporter.get_finished_spans() if span.name == "agentic.artifact"
    ]
    assert [span.attributes["agentic.receipt.hit"] for span in role_spans] == [False, True]
    assert (
        role_spans[0].attributes["agentic.operation.id"]
        == role_spans[1].attributes["agentic.operation.id"]
    )
    assert len(artifact_spans) == 1
