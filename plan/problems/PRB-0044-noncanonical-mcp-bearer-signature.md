# PRB-0044 — Non-canonical MCP bearer signature encoding

Status: resolved

Date: 2026-09-14

## Symptom and reproduction

Adversarial test изменил последний Base64URL-символ HMAC signature, но token остался валидным:
неиспользуемые padding bits позволяли разным строкам декодироваться в одинаковые signature bytes.

## Cause

Verifier проверял допустимый alphabet и HMAC bytes, но не требовал canonical unpadded Base64URL.

## Fix and regression

После strict decode verifier заново кодирует bytes и требует точного совпадения с исходным segment.
Parameterized `test_bearer_rejects_cross_scope_and_tampering_before_gateway` теперь отклоняет
изменённый segment до вызова underlying gateway.
