# Авторство, вычитка и техническая проверка

## Глубина и согласованность

Определение → причинность → предпосылки → альтернатива → контрпример. Русская техническая
проза, deep theory вместо default «101». Primary owner и prerequisites предотвращают повторение.
Пример ограничен code/dated evidence. Нет student labs, setup или implementation tasks.

## Skills и availability

- `technical-markdown-lectures`: доступен; структура и техническая проза.
- [technical-editorial-review](skills/technical-editorial-review/SKILL.md): создан и локально установлен;
  отдельная полная вычитка структуры, языка, терминологии и дублирования.
- [technical-claim-verification](skills/technical-claim-verification/SKILL.md): создан и локально установлен;
  отдельная проверка primary sources/code/evidence и diagram semantics.
- `skill-creator`: применён для подготовки пакетов, не подмена review.
- `openai-docs`: условно обязателен для OpenAI-specific claims, не универсальный источник по GateLLM.

Versioned packages — course/skills, локальные copies — ~/.codex/skills. Другой contributor сначала
подготавливает доступные copies, читает полные инструкции и records versions. Наличие файла
не означает фактическое применение skill. No delegation/publication/paid calls implied by review.

## Проходы после каждого текста

1. Авторство по todo/outcomes/owners и [technical requirements](technical-requirements.md).
2. Отдельная полная редакторская вычитка после написания.
3. Technical verification: definitions/causality/API/numbers/code/evidence/diagrams.
4. Corrections + recheck; major rewriting требует полной повторной вычитки.
5. При diagrams — actual render/visual gate; отсутствующий renderer не получает PASS.
6. Актуальный receipt без unresolved major/blocking findings, затем reviewed.

Один автор может выполнять разные проходы, но это не независимый review. Checker проверяет
формат и input freshness, не истинность prose или полноту человеческой проверки.

## Records

[Review schema](templates/review.json), [guide](templates/review.md).
Digest включает текст/assets, план и source mapping, требования/glossary, skills, config/toolchain.
Изменение inputs делает receipt stale. Outlines не получают fake receipts.
Статусы: outline → draft → editorial-reviewed → technically-verified → reviewed.
