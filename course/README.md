# Multi-Agent Engineering: теоретический курс

Глубокая теоретическая база для Data Engineers с Python/SQL и знанием pipelines.
Наша Agentic Data Platform — иллюстрация подтверждённых решений, не student lab.
Подготовлены 26 core outlines и optional Kubernetes extension. Написаны и опубликованы лекции 00/01/02/03;
остальные 23 текста ещё не написаны. Для каждого текста действует отдельный publication gate;
полный текст выбирается reader только по reviewed и актуальным receipts.
Manager/Kubernetes не объявляются реализованными.
В core номер 00–25 равен позиции в маршруте; optional Kubernetes — 26.
Соответствие прежним тематическим IDs зафиксировано в [STEP-0034](../plan/steps/STEP-0034-course-sequential-numbering.md).

- [Syllabus](syllabus.md) и [canonical manifest](manifest.json)
- [Todo-планы](../plan/steps/lections/README.md) и [директория текстов](lectures/README.md)
- [Source-index](source-index.md), [source registry](sources.json), [glossary](glossary.md)
- [Редакторские правила](editorial-guidelines.md), [технические требования](technical-requirements.md)
- [Статус HTML/SVG-сборки](build-status.md)
- [Принятый дизайн сайта](design/site-design.md): Cyberpunk landing, SVG roadmap,
  меню модулей/лекций слева и TOC справа. STEP-0028 реализует UI прототипа:
  вместо ещё не написанных лекций отображаются существующие Markdown-планы тем.

Contributor command: `make course-check` — offline metadata/Markdown/receipt checks, не
фактчекинг и не проверка model quality. `make course-build` собирает проверочный прототип,
публикует только проверенные тексты, остальные темы остаются outlines.
Кандидат: `make course-review COURSE_LECTURE=0` в отдельном labelled output.
Установка renderer: `make course-renderer-install`; просмотр:
`make course-preview` → http://127.0.0.1:8099/course/. Python окружение: `make bootstrap`.
Для рендеринга нужны Ubuntu fonts с Noto Sans и fontconfig; fingerprint системного шрифта
фиксируется отдельно от поставляемых локальных web fonts.
Нет labs, coding assignments, submissions или capstone-задания; часы оцениваются после пилота.
