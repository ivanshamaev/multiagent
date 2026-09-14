import pytest
from pydantic import ValidationError

from runtime.telemetry import OTLPHTTPConfig, build_otlp_telemetry


@pytest.mark.parametrize(
    "endpoint",
    ["http://127.0.0.1:4318", "http://localhost:14318/"],
)
def test_otlp_config_accepts_explicit_loopback_origin(endpoint: str) -> None:
    assert OTLPHTTPConfig(endpoint=endpoint).endpoint == endpoint


@pytest.mark.parametrize(
    "endpoint",
    [
        "https://127.0.0.1:4318",
        "http://collector:4318",
        "http://0.0.0.0:4318",
        "http://127.0.0.1",
        "http://user:password@127.0.0.1:4318",
        "http://127.0.0.1:4318/v1/traces",
        "http://127.0.0.1:4318?token=unsafe",
    ],
)
def test_otlp_config_rejects_nonlocal_or_ambiguous_endpoints(endpoint: str) -> None:
    with pytest.raises(ValidationError, match="loopback HTTP origin"):
        OTLPHTTPConfig(endpoint=endpoint)


def test_otlp_factory_is_explicit_and_does_not_set_global_provider() -> None:
    from opentelemetry import trace

    before = trace.get_tracer_provider()
    telemetry = build_otlp_telemetry(OTLPHTTPConfig(timeout_seconds=1))
    try:
        assert telemetry.provider is not before
        assert trace.get_tracer_provider() is before
    finally:
        telemetry.shutdown()
