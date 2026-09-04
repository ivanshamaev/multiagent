# ADR-0007 — Курс из доказанной практики

Status: accepted  
Date: 2026-09-04

## Context

Цель репозитория — не только reference system, но и практический advanced-курс. Теоретический syllabus до экспериментов не покажет реальные failure modes и trade-offs.

## Decision

Сначала создаём рабочую систему, benchmark suite и каталог ошибок. После v1 формируем лекции из ADR, changes, traces, metrics, failed experiments и regression fixes. Каждая практика воспроизводит реальную проблему и проверяется hidden tests.

## Alternatives

Параллельное написание полного курса отклонено; до v1 допускается только сохранение учебно значимых evidence и заметок.

## Consequences and validation

Нужно дисциплинированно вести `plan/`. Глава готова, только если ссылается на воспроизводимый scenario, наблюдаемую ошибку, применённое решение и измеримый результат.

