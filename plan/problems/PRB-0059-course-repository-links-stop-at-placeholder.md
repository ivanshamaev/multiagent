# PRB-0059 — Course repository links stop at a placeholder index

Status: resolved

Date: 2026-09-19

## Reproduction

1. Открыть опубликованную ссылку
   `references.html#ref-84600c447037` из лекции 18.
2. Страница показывает путь `policies/profiles/airflow_observer_v1.json` и
   сообщение «Материал доступен в checkout», но не даёт открыть файл.
3. Локальная production build содержит 212 таких links на 105 уникальных
   repository paths; затронуты все 27 lecture pages.

## Причина

`course/build.py` считает любой относительный target, которого нет в карте
публикуемых course pages, repository reference. Вместо repository browser URL
он создаёт hash anchor `references.html#ref-<sha12>`. Генератор
`references.html` выводит path в `<dt>` и статическую заглушку в `<dd>`, без
`<a href>`. Fragment для repository target при этом также теряется. Тесты
проверяли внутреннюю целостность build, но не destination repository links.

## Исправление и regression

Repository target должен преобразовываться в URL public GitHub blob на
публикуемом `main`, с percent-encoded path и сохранённым fragment. Reference
index использует тот же helper и остаётся allowlisted metadata page; исходные
repository files в site не копируются. Regression покрывает direct lecture
link, fragment, clickable index и отсутствие placeholder routing.

## Предел исправления

Build-time проверка подтверждает, что local target существует на собираемом
commit. Она не гарантирует, что `main` никогда не изменится после публикации,
и не заменяет внешний link monitor. Immutable commit URLs могут быть отдельной
политикой provenance, если курс перестанет следовать current `main`.

## Проверка исправления

Builder преобразует repository targets в прямые GitHub blob URLs, сохраняет
fragments и отклоняет absolute/traversal paths. В production build найдено
212 прямых repository links и ни одного `references.html#ref-*` на страницах
лекций; index содержит 107 кликабельных paths. Две production-сборки
побайтно совпали. Regression и полный repository gate зафиксированы в
`plan/evidence/STEP-0059-github-repository-links.md`.
