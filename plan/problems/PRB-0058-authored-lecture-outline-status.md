# PRB-0058 — Reader называл подготовленный текст ненаписанным

Status: resolved

Date: 2026-09-15

## Reproduction и причина

Передать `course.site.outline` manifest entry со статусом `draft` либо
`technically-verified`. Reader продолжал выдавать «текст лекции не написан»:
подпись была hardcoded для первоначального каркаса, где все тексты отсутствовали.

## Исправление и regression

Отображать отсутствие текста только для `outline`; для authored statuses
выводить «текст подготовлен, но не опубликован». Сам reader по-прежнему
собирает outline, а не не прошедшую publication gate лекцию.

`test_outline_reader_does_not_claim_authored_text_is_unwritten` проверяет четыре
authored statuses, отсутствие старой подписи и сохранение outline content.
Команды и результаты final verification — в evidence STEP-0029.
