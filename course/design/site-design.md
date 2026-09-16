# Дизайн сайта курса

Status: accepted specification; prototype UI implemented in STEP-0028.

Зафиксировано 2026-09-15 по запросу пользователя и
[Cyberpunk / Glitch reference](cyberpunk-glitch-reference.txt).
[ADR-0038](../../plan/decisions/ADR-0038-course-landing-roadmap-reader-design.md).

## Информационная архитектура

Главная — landing про глубокий теоретический курс multi-agent systems для Data Engineering.
Далее пользователь переходит к модулям и лекциям. Наш мультиагент — сквозной инженерный пример;
лабораторные, практические задания и вымышленные результаты обучения не добавляются.

- Landing: назначение курса, аудитория/prerequisites, чему посвящена теория,
  два подхода к orchestration, пример Agentic Data Platform, roadmap и программа.
- Module page: описание тематического блока, список лекций, prerequisites и их статусы.
- Lecture page: текст Markdown, встроенные SVG, источники, итоги и концептуальные вопросы.
- Technical requirements/repository references/prototype — служебные страницы,
  не основной пользовательский landing. При реализации сохранить доступ к prototype отдельно.

## Главная: landing

Hero с разделением примерно 60/40: слева название, короткое обещание содержания и CTA
«Смотреть программу» / «Открыть маршрут»; справа — техническая SVG-композиция команды агентов.
Не выдавать декоративную архитектуру за trace выполненного runtime.

Далее: аудитория и входные знания → темы и результаты понимания → SVG roadmap →
каталог модулей → наша reference system и границы доказанного → FAQ о формате/готовности.
Terminal panel показывает структуру курса, не имитирует платёж, live run или student progress.
Нет выдуманных отзывов, сроков, цен и обещаний сертификата. «Начать чтение» появляется только
при наличии допустимого к публикации текста; outline имеет честную ссылку на план/описание.

## Desktop: страницы модулей и лекций

```text
┌────────────────────────────────────────────────────────────────────────┐
│ Логотип / курс             Программа · Roadmap · О курсе                │
├─────────────────┬──────────────────────────────────┬───────────────────┤
│ ПРОГРАММА КУРСА │ Breadcrumbs / модуль / статус     │ В ЭТОЙ ЛЕКЦИИ     │
│ Модули          │ Название лекции                  │ Разделы H2        │
│   Лекции        │ Prerequisites / введение         │ Подразделы H3     │
│   Текущая ←     │ Текст · SVG · примеры · источники│ Текущий раздел ←  │
│ Optional track  │ Итоги / предыдущая / следующая   │                   │
└─────────────────┴──────────────────────────────────┴───────────────────┘
```

Слева — course navigation с модулями и вложенными лекциями, раскрытие текущего модуля,
маркер активной страницы и статусы. Справа — TOC текущей лекции из AST H2/H3, а не второй
список лекций; anchor links, `aria-current`, подсветка раздела как JS enhancement.
На module page справа можно показывать разделы её описания; на landing sidebar не требуется.

Desktop от 1280px: shell до 1600px, левая колонка около 260px, текст 680–820px,
правое TOC около 220px, gutters 24px. Это layout targets, не жёсткая ширина viewport.
Sidebars sticky с собственным scroll при необходимости; не перекрывают header/anchors.
Внизу — предыдущая/следующая в canonical teaching_order; core ID совпадают с порядком.

## SVG roadmap курса

Roadmap генерируется при build из [manifest](../manifest.json), не поддерживается вручную
как второй curriculum. Узлы: lecture ID, краткая тема, track и реальный editorial status.
Группы показывают тематические блоки; соответствие групп фиксируется отдельно, без
повторной перенумерации outlines. Core включает 26 тем, extension 26 отделён визуально.

Сплошной маршрут — рекомендованный teaching_order; пунктирные prerequisites — другой тип
связи с явной легендой. Если dependency edges перегружают обзор, показать их в текстовом
списке выбранной темы, а не рисовать нечитаемый полный граф. Не маркировать outline как completed.

Узел ведёт на реально существующий module/lecture URL, доступен клавиатурой;
SVG имеет title/desc и namespace IDs. Рядом — обычный HTML ordered list с теми же ссылками:
курс доступен без JS и без интерпретации цвета. Масштаб/reset/fullscreen переиспользуют
проверенный viewer; на mobile допустим local scroll/vertical roadmap, не page overflow.
Новый linked-roadmap SVG профиль проверяется отдельно: не ослаблять Mermaid sanitizer глобально.

## Визуальные tokens

Все значения централизованы в CSS custom properties, без одноразовых inline styles.

| Token | Значение / роль |
| --- | --- |
| background | `#0a0a0f`, обязательная тёмная оболочка |
| foreground | `#e0e0e0`, основной текст |
| card / input | `#12121a` |
| muted | `#1c1c2e`, технические панели |
| mutedForeground reference | `#6b7280`, только после contrast check для выбранной роли |
| readable secondary candidate | `#9aa3b2`, отдельно проверяется перед реализацией |
| accent / ring | `#00ff88`, CTA, active/focus |
| accentSecondary | `#ff00ff`, вторичный выразительный акцент |
| accentTertiary | `#00d4ff`, ссылки/roadmap связи |
| border | `#2a2a3a`; interactive boundary при необходимости усиливается |
| destructive | `#ff3366`; статус сопровождается текстом/значком |

Базовая сетка 8px; borders 1px, emphasis 2px. Панели/CTA со срезанными углами около 10px,
обычный radius 0–2px, input до 4px. Clip-path не должен обрезать focus ring:
декоративный wrapper отделён от интерактивного элемента. Неоновые shadows — для CTA,
active state и hero, не для каждой строки. Статусы не кодируются одним цветом.

## Типографика и читаемость

Reference: Orbitron/Share Tech Mono для display, JetBrains Mono/Fira Code для body/code.
Перед установкой проверить лицензии, кириллицу, glyph coverage и pin локальных font assets.
Для русских заголовков задать проверенный кириллический fallback, включая существующий Noto Sans.
Не загружать Google Fonts/CDN в браузере. Без загрузки web fonts текст остаётся читаемым.

Hero display uppercase с широкой разрядкой: ориентир 48px mobile → 72–96px desktop.
Текст лекции 17–18px, line-height 1.65–1.8; H2 около 28–36px. Body не uppercase,
не letter-spaced как terminal labels и не светится. Moноширинность не оправдывает длинную
строку: приоритет читаемого measure, таблицы/code/SVG прокручиваются локально.
Обязательная тёмная тема относится к экрану; print — светлый, без декоративных эффектов.
Цвет SVG canvas выбирается по читаемости labels/стрелок, не принудительным CSS invert.

## Эффекты: адаптация reference к учебному сайту

Сохраняются RGB split hero, bounded glitch animation, subtle scanlines/grid/circuit pattern,
terminal prefix/cursor, chamfered panels и stacked neon glow. Асимметрия и перекрытия —
в декоративных hero/landing элементах, не в тексте, TOC или технических диаграммах.

Glitch/cursor animation ограничена коротким вступлением; затем статичная композиция.
Нет бесконечного мерцания или scanline scrolling поверх лекции. Scanline layer не перехватывает
pointer events и не снижает читаемость article. `prefers-reduced-motion` отключает движение;
статичный RGB accent допустим только при читаемом заголовке. Контент не появляется лишь
после typewriter/animation. Hover — короткий border/glow эффект, без скачков layout.

Это явное уточнение исходных perpetual blink/glitch и «all transition» recipes:
образ сохранён, длительное чтение и доступность важнее декоративной интенсивности.

## Responsive и доступность

- 768–1279px: course sidebar + текст; TOC переносится в раскрываемый блок над текстом.
- До 768px: одна колонка; «Программа курса» и «В этой лекции» — два раздельных disclosure
  блока перед article, доступные без JS. Если позже drawer — Escape/focus return обязателен.
- Проверять 360/768/1280/1600px, long Russian headings, keyboard, zoom, print и no-JS.
- Touch targets ориентир ≥44px, visible focus, skip link, semantic nav/main/article/aside.
- Контраст каждого значимого текста/контрола проверяется на фактическом background.
  Утверждение reference «все цвета AA» не принимается как измерение.
- Roadmap и боковые меню не заменяют последовательное чтение/HTML fallback.

## Реализация и приёмка: отдельный следующий шаг

Сначала tokens/fonts/layout primitives → landing → manifest-driven module navigation/roadmap
→ AST TOC/reader → mobile/no-JS/print → browser screenshots и визуальная проверка.
Использовать текущие Python templates + external CSS/JS; React/Tailwind не требуются.
Нужны regression tests URL/status/order/TOC/linked SVG, two-build checks, строгий CSP,
отсутствие private checkout files в output и `make check`.

Нельзя открывать для публикации unreviewed lecture только ради заполнения нового layout.
Дизайн не меняет per-lecture editorial/technical/visual/recheck gates. Эта спецификация принята;
STEP-0028 реализует landing/roadmap/reader для существующих Markdown outlines, не публикует
полные тексты. Noto Sans — локальный кириллический шрифт reader; terminal labels используют
системный monospace. Установка display fonts reference остаётся отдельным refinement.
