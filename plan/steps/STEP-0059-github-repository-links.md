# STEP-0059 — Course publication: прямые ссылки на repository examples

Status: complete

Owner: Codex

Updated: 2026-09-19

## Цель и границы

Исправить static course builder так, чтобы относительные ссылки из лекций
на code/evidence вне `course/` открывали соответствующие public files в
GitHub repository, а не некликабельные anchors страницы `references.html`.
Сохранить fragments, containment checks и запрет копирования checkout в
public output. Сделать сам `references.html` кликабельным индексом.

Не менять исходный текст лекций, содержательные reviews или доказательные
границы курса. Repository browser ref — `main`, совпадающий с branch,
публикуемым GitHub Pages workflow. Изменение builder требует обновить только
publication receipts всех 27 лекций и повторить static gates.

## Критерии приёмки

- [x] Воспроизвести `ref-84600c447037` и зафиксировать причину в PRB-0059.
- [x] Repository links преобразуются в
  `https://github.com/ivanshamaev/multiagent/blob/main/<encoded-path>`.
- [x] URL fragment сохраняется; course-local links продолжают указывать на
  generated HTML, внешние HTTPS links не меняются.
- [x] `references.html` содержит кликабельные repository paths без публикации
  файлов checkout.
- [x] Regression tests проверяют direct link, fragment, index и отсутствие
  прежнего `references.html#ref-*` в lecture output.
- [x] Все 27 publication receipts механически обновлены для нового builder и
  rendered HTML; content receipts не изменены.
- [x] Candidate/static build, две production builds, `make check`, link audit
  и `git diff --check` проходят.

## Риски

Ссылка на `main` отражает текущую версию repository, а не immutable snapshot;
это сознательно соответствует опубликованному Pages branch. Переименование
или удаление файла позднее может сломать URL, поэтому build проверяет локальное
существование target, а regression — форму преобразования. Изменение
`course/build.py` инвалидирует publication digests всех лекций независимо от
того, сколько ссылок изменилось.

## Work log

2026-09-19: live Pages и локальная production build подтверждают 212 ссылок
на 105 repository paths во всех 27 лекциях. Конкретный ref пользователя
соответствует `policies/profiles/airflow_observer_v1.json`; GitHub blob URL
доступен с HTTP 200. Существующий STEP-0056 CI/CD не изменяется; до завершения
этой работы governance временно видит два `in progress` шага.

2026-09-19: добавлен единый path-safe URL helper; fragment сохраняется,
reference index стал кликабельным. Обновлены 27 publication receipts в
text-only scope без переноса прежних visual claims. Candidate build,
targeted tests и две идентичные production builds прошли. Итоговый полный
gate и команды записаны в evidence; STEP-0056 остаётся единственным активным
шагом и не менялся.
