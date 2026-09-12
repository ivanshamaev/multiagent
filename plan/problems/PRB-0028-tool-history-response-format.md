# PRB-0028 — Tool-history finalization rejected provider schema mode

- Status: resolved
- Detected: 2026-09-12
- Scope: GateLLM/Llama phased final response

## Reproduction and cause

With parallel calls disabled, the investigation phase completed exactly one allowed
`workspace.read_file`. MAF then requested its final response with the accumulated tool history,
tools disabled, and `response_format`; GateLLM returned HTTP 400. Earlier plain multi-round tool
probes succeeded, isolating the incompatible parameter combination.

## Fix and regression check

Tool-enabled phases describe the exact JSON schema in the trusted prompt and validate the returned
text locally with closed Pydantic models. Provider schema mode remains mandatory for tool-free calls
and capability probing, but is omitted from tool-history requests. Unit tests lock this separation;
the live record proves the first tool call remains singular and policy-authorized.
