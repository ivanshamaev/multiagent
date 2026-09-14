from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_observability_services_never_receive_gateway_token_or_environment_file() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    observability = compose[compose.index("  otel-collector:") : compose.index("\nvolumes:")]
    assert "API_TOKEN" not in observability
    assert "env_file:" not in observability


def test_collector_does_not_derive_metrics_from_sensitive_content_or_identifiers() -> None:
    collector = (ROOT / "observability/otel-collector.yaml").read_text(encoding="utf-8")
    lowered = collector.lower()
    for forbidden in (
        "prompt",
        "completion",
        "exception.message",
        "tool.arguments",
        "tool.output",
        "workflow.id",
        "task.id",
        "request.id",
        "artifact.id",
    ):
        assert forbidden not in lowered
