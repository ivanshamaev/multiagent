# TODO — Лекция 03. Harness и инженерия контекста одного вызова

Status: reviewed

Updated: 2026-09-16

Текст: `course/lectures/LECTURE-0003-harness-context.md`.

Track: core; исходная тема init: 04.

## Цель и уникальная область

Объяснить per-turn context selection; model-provider abstraction; structured response boundary: модель, условия применимости, ограничения и контрпримеры.
Эта лекция — primary owner указанных concepts; определения из других лекций не повторять.

Prerequisites: [02](LECTURE-0002-contracts.md).

## Что писать — todo

- [x] Разделить harness loop, transport adapter и domain logic.
- [x] Объяснить selection/compaction и token-relevant information на уровне текущего вызова.
- [x] Сопоставить prompt, retrieved material и tool results без повторения storage consistency.
- [x] Разобрать structured response и error handling; persistent recovery и экономику отправить владельцам.
- [x] Добавить полезную схему/таблицу, строгие предпосылки и хотя бы один контрпример без laboratory exercise.
- [x] Завершить кратким резюме, 3–5 концептуальными self-check questions и переходом по syllabus.

## Границы и согласованность

Не пересказывать theory владельцев: [04](LECTURE-0004-state-memory.md), [17](LECTURE-0017-recovery-idempotency.md), [23](LECTURE-0023-cost-performance.md).
Перед использованием заимствованного термина ссылаться на его primary owner из [карты](README.md).
Повторный case разрешён только с новым аналитическим вопросом; заново объяснять предыдущий case нельзя.
Лекция theory-only: нет student setup, coding tasks, обязательного запуска команд или сдачи работы.

## Иллюстрация нашей системой

runtime/context.py; runtime/model_provider.py; STEP-0007.

- [x] Проверить code/evidence anchors и подписать historical/offline/not-implemented boundaries.
- [x] Не расширять фактические claims до fully-live READY, autonomous merge или planner runtime, которого нет.

## Интернет-статьи и переиспользуемые идеи

- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) (Anthropic, S07). Идея для этого ракурса: Отбор ограниченного полезного контекста.
- [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) (Anthropic, S30). Идея для этого ракурса: Progressive disclosure знаний, не реализация runtime skills.

- [x] Перед авторством перечитать выбранные разделы; точные claims/API details проверить по первичным источникам.
- [x] Переиспользовать концепции своими словами с attribution; не копировать текст, полный перевод или чужую схему.
- [x] Различить утверждение статьи, наш пример и авторское обобщение; source caveats — в [SOURCES](SOURCES.md).

## Авторство, редактура и фактчекинг — обязательные todo

- [x] Соблюсти [технические требования](../../../course/technical-requirements.md): Markdown и Mermaid с подписью, accTitle/accDescr и текстовым эквивалентом.
- [x] При готовом сборщике проверить SVG/HTML визуально: стрелки, кириллицу, mobile/desktop, no-JS и доступность; не отмечать render PASS до фактической проверки.
- [x] В review учесть diagram config/toolchain/assets; не повторять UI-код zoom/pan/fullscreen в тексте лекции.

- [x] Применить `technical-markdown-lectures` с deep-theory depth; созданные editorial skills прочитать перед review и записать версии/usage.
- [x] После написания выполнить полную вычитку: язык, терминология, структура, повторы внутри лекции и по соседним темам.
- [x] Отдельно перепроверить существенные claims, числа/даты/версии, соответствие схем тексту и code/evidence.
- [x] Исправить findings и повторно проверить затронутый текст; существенная переработка требует полной вычитки.
- [x] Сохранить per-lecture review record с content hash и source anchors; missing/stale review запрещает reviewed.
- [x] Перед публикацией сверить topic ownership/cross-links и отсутствие unresolved существенных замечаний.

Review: `course/reviews/LECTURE-0003.json`; candidate reader gate — `output/playwright/step33/lecture-4/`.
Вычитка и техническая проверка выполнены отдельными проходами. Исправлены две
неточности о metadata файла и доверии к prompt-маркерам; полный текст перечитан.
Проверены desktop/mobile, light/dark, print, no-JS, keyboard/AX, CSP и локальные
ссылки; семь скриншотов просмотрены вручную. Реальное assistive technology не тестировалось.
