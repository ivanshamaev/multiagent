"""Validated, redacted configuration for the local GateLLM runtime."""

from __future__ import annotations

from typing import Annotated
from urllib.parse import urlsplit

from pydantic import Field, SecretStr, StringConstraints, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ModelIdentifier = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=200,
        pattern=r"^[~A-Za-z0-9][A-Za-z0-9._:/-]*$",
    ),
]


class GateLLMSettings(BaseSettings):
    """Load only the explicit GateLLM settings used by the local control plane."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )

    api_token: SecretStr = Field(validation_alias="API_TOKEN", repr=False, exclude=True)
    base_url: str = Field(
        default="https://gatellm.ru/v1",
        validation_alias="LLM_BASE_URL",
    )
    default_model: ModelIdentifier | None = Field(
        default=None,
        validation_alias="LLM_DEFAULT_MODEL",
    )
    request_timeout_seconds: float = Field(
        default=30,
        gt=0,
        le=120,
        validation_alias="LLM_REQUEST_TIMEOUT_SECONDS",
    )
    max_output_tokens: int = Field(
        default=512,
        ge=1,
        le=4096,
        validation_alias="LLM_MAX_OUTPUT_TOKENS",
    )
    max_retries: int = Field(
        default=1,
        ge=0,
        le=3,
        validation_alias="LLM_MAX_RETRIES",
    )

    @field_validator("api_token")
    @classmethod
    def validate_api_token(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().strip():
            raise ValueError("API_TOKEN must not be empty")
        return value

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, value: str) -> str:
        normalized = value.rstrip("/")
        parsed = urlsplit(normalized)
        if (
            parsed.scheme != "https"
            or parsed.hostname != "gatellm.ru"
            or parsed.path != "/v1"
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("LLM_BASE_URL must be exactly the HTTPS GateLLM /v1 endpoint")
        return normalized
