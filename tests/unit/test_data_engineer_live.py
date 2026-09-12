import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from runtime.data_engineer_live import (
    _aggregate_model_calls,
    _configuration_fingerprint,
    _estimated_cost,
    _load_capability_cache,
    _persist_capability_cache,
    _persist_run_record,
)
from runtime.model_provider import (
    AvailableModel,
    ModelCallRecord,
    ModelCapabilityProbe,
    ModelCatalogSnapshot,
    ModelPricing,
    ModelsResponse,
    ModelUsage,
)


def test_live_metadata_is_deterministic_and_cost_uses_catalog_prices() -> None:
    first = _configuration_fingerprint(
        budget_limits={"model_tokens": 42_000, "rework_attempts": 2},
        model_id="fake/cheap",
        profile_payload={"allowed_tools": ["workspace.read_file"]},
        scenario_id="net-revenue",
        scenario_version="1.0.0",
    )
    second = _configuration_fingerprint(
        budget_limits={"model_tokens": 42_000, "rework_attempts": 2},
        model_id="fake/cheap",
        profile_payload={"allowed_tools": ["workspace.read_file"]},
        scenario_id="net-revenue",
        scenario_version="1.0.0",
    )

    assert first == second
    assert len(first) == 64
    changed_budget = _configuration_fingerprint(
        budget_limits={"model_tokens": 30_000, "rework_attempts": 2},
        model_id="fake/cheap",
        profile_payload={"allowed_tools": ["workspace.read_file"]},
        scenario_id="net-revenue",
        scenario_version="1.0.0",
    )
    assert changed_budget != first
    assert _estimated_cost(1_000, 500, Decimal("5.1"), Decimal("33.6")) == "0.021900"


def test_phased_model_metadata_is_aggregated_without_raw_content() -> None:
    calls = tuple(
        ModelCallRecord(
            model_id="fake/cheap",
            usage=ModelUsage(input_tokens=index, output_tokens=1, total_tokens=index + 1),
            latency_ms=index * 10,
            finish_reason="stop",
            request_sha256=str(index) * 64,
            response_sha256=chr(96 + index) * 64,
        )
        for index in (1, 2)
    )

    usage, latency_ms, request_hash, response_hash = _aggregate_model_calls(calls)

    assert usage == ModelUsage(input_tokens=3, output_tokens=2, total_tokens=5)
    assert latency_ms == 30
    assert len(request_hash) == 64
    assert len(response_hash) == 64


def test_run_record_is_private_and_contains_no_prompt_or_token(tmp_path, monkeypatch) -> None:
    import runtime.data_engineer_live as live

    monkeypatch.setattr(live, "REPOSITORY_ROOT", tmp_path)
    record = {
        "workflow_id": "de-net-revenue-test",
        "model_id": "fake/cheap",
        "usage": {"total_tokens": 10},
    }

    relative = _persist_run_record("de-net-revenue-test", record)
    target = tmp_path / relative
    contents = target.read_text(encoding="utf-8")

    assert json.loads(contents) == record
    assert target.stat().st_mode & 0o777 == 0o600
    assert "prompt" not in contents
    assert "API_TOKEN" not in contents

    with pytest.raises(RuntimeError, match="unsafe"):
        _persist_run_record("../escape", record)


def test_capability_cache_is_private_ttl_and_catalog_bound(tmp_path, monkeypatch) -> None:
    import runtime.data_engineer_live as live

    monkeypatch.setattr(live, "REPOSITORY_ROOT", tmp_path)
    model = AvailableModel(
        id="fake/cheap",
        object="model",
        created=1,
        owned_by="provider",
        name="Cheap",
        description="test",
        context_length=10_000,
        category="CHAT",
        pricing=ModelPricing(prompt=Decimal("1"), completion=Decimal("2")),
    )
    snapshot = ModelCatalogSnapshot(
        retrieved_at=datetime.now(UTC),
        catalog=ModelsResponse(object="list", data=(model,)),
    )
    schema_probe = ModelCapabilityProbe(model_id=model.id, status_code=200, available=True)
    tool_probe = ModelCapabilityProbe(model_id=model.id, status_code=200, available=True)

    _persist_capability_cache(snapshot, model, schema_probe, tool_probe)
    cached = _load_capability_cache(snapshot, model.id, now=datetime.now(UTC))

    assert cached is not None
    assert cached[0] == model
    cache_path = tmp_path / ".scenario-state/model-capability.json"
    assert cache_path.stat().st_mode & 0o777 == 0o600
    assert (
        _load_capability_cache(
            snapshot,
            model.id,
            now=datetime.now(UTC) + timedelta(hours=2),
        )
        is None
    )
    changed = snapshot.model_copy(
        update={
            "catalog": ModelsResponse(
                object="list",
                data=(
                    model.model_copy(
                        update={"pricing": ModelPricing(prompt=Decimal("2"), completion=2)}
                    ),
                ),
            )
        }
    )
    assert _load_capability_cache(changed, model.id, now=datetime.now(UTC)) is None
