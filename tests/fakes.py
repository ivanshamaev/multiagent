"""Reusable offline fakes for model-provider and workflow tests."""

from agent_framework import BaseChatClient, ChatResponse, Message

from runtime.context import ContextBundle, ContextDocument
from runtime.settings import GateLLMSettings

TEST_API_TOKEN = "unit-test-token"


def gate_settings(**updates) -> GateLLMSettings:
    values = {
        "api_token": TEST_API_TOKEN,
        "default_model": "fake/cheap-model",
        "max_output_tokens": 128,
        "max_retries": 0,
    }
    values.update(updates)
    return GateLLMSettings(_env_file=None, **values)


def context_bundle() -> ContextBundle:
    content = "# Synthetic task\n"
    return ContextBundle(
        workspace_fingerprint="b" * 64,
        documents=(
            ContextDocument(
                path="TASK.md",
                content=content,
                size_bytes=len(content.encode()),
                sha256="dbc9b06435eb3c02b2a3d51c6c364ee15b2346b37b2e1a153d7d83fc271227b7",
            ),
        ),
        total_bytes=len(content.encode()),
    )


class StaticChatClient(BaseChatClient):
    def __init__(self, payload: str) -> None:
        super().__init__()
        self.payload = payload
        self.messages = ()
        self.options = {}

    async def _inner_get_response(self, *, messages, stream, options, **kwargs):
        assert stream is False
        self.messages = tuple(messages)
        self.options = dict(options)
        return ChatResponse(
            messages=Message("assistant", [self.payload]),
            finish_reason="stop",
            usage_details={
                "input_token_count": 10,
                "output_token_count": 5,
                "total_token_count": 15,
            },
        )
