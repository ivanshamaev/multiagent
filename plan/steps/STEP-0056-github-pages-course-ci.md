# STEP-0056: GitHub Actions CI/CD сборки курса в GitHub Pages

Status: in progress

## Scope

Организовать сборку теоретического курса (`course/`) в GitHub Actions и публикацию
статического сайта в GitHub Pages.

## Acceptance

- Workflow `.github/workflows/course-pages.yml` запускается на push в `main` с путями
  `course/**` и вручную (`workflow_dispatch`).
- Сборка детерминирована: используется pinned системный Noto Sans
  (`course/fonts/NotoSans-Regular.ttf`, SHA-256 проверяется и устанавливается в
  `/usr/share/fonts`), locked renderer (`make course-renderer-install`) и frozen
  Python-окружение (`make bootstrap`, uv lock).
- Перед сборкой выполняются `make course-check`; сборка — `make course-build`.
- Артефакт `build/course` публикуется через `actions/upload-pages-artifact` +
  `actions/deploy-pages` в GitHub Pages.

## Risks

- Publication receipts содержат fingerprint системного шрифта и Chromium; любое отличие
  версии шрифта на раннере отклоняется сборкой (`publication renderer fingerprint
  mismatch`) — поэтому шрифт зафиксирован в репозитории (SIL OFL 1.1, переиздание
  разрешено лицензией).
- GitHub-hosted runner может получить обновлённый Chromium из puppeteer cache
  официального pinned релиза; расхождение версий браузера не входит в fingerprint
  сравнение по хэшу, но SVG-рендер завязан на pinned `chromium` в `package-lock.json`.
- Требуется настройка Pages: Source = GitHub Actions в настройках репозитория.

## Verification

- Локально: `make course-check`, `make course-build` на Ubuntu 24.04 с тем же шрифтом.
- CI: запуск workflow на push; зелёные job'ы `build` и `deploy`, сайт доступен по URL Pages.
