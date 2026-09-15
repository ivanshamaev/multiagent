# ADR-0039 — Per-lecture publication receipts

Status: accepted

Date: 2026-09-15

## Контекст

Prototype builder показывал только outlines; content review не проверял
полную лекцию в финальном reader. Одного global renderer flag недостаточно
для публикации нового текста или после изменения CSS/JS/builder.

## Решение

Content receipt остаётся отдельным. `reviewed` дополнительно требует publication
receipt с привязкой к content review и publication implementation inputs,
реальному toolchain fingerprint и per-lecture browser/visual passes.
Обычная сборка не принимает technically-verified как published. Candidate build
разрешает такие тексты только в отдельном labelled output.

URL `topic-NNNN.html` неизменен: до принятия — outline, после — полный текст.
Markdown AST отвечает за anchors, TOC и SVG; repository references остаются
metadata, не копией checkout. Outline cross-links сохраняют стабильные URLs.

Freshness fingerprint включает source review, builder, site generator, gate code,
CSS/JS, parser/renderer lockfiles и config. Browser artifact hashes сохраняются
как provenance; checker не доказывает, что reviewer действительно выполнил
проверки. Receipt — trusted contributor record, не LLM input.

Screen-reader доступность проверяется через AX tree, accessible names/descriptions,
semantic landmarks и текстовые эквиваленты в no-JS HTML. Это не реальная проверка
Orca/NVDA/VoiceOver; interoperability проверка отдельно записывается как непройденная
и остаётся deployment risk. Viewport, keyboard, print, CSP и визуальные проверки
выполняются реально, не по исходнику.

## Последствия

Изменение публикационного кода делает receipts stale и требует browser recheck.
Renderer `verified` характеризует проверенный toolchain, не готовность всех лекций.
Непроверенный текст не публикуется автоматически. Курс остаётся local static HTML
без новых CDN/frameworks/backend и лабораторных работ.
