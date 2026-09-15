# PRB-0054 — Fullscreen Escape depended on browser chrome shortcut

Status: resolved

Date: 2026-09-15

## Reproduction и cause

Real CLI browser-check entered fullscreen, then `page.keyboard.press('Escape')` did not end it;
waitForFunction timed out after 30s. Viewer handled Escape for CSS fallback only and relied on
native browser chrome behaviour, which is not guaranteed for headless/CDP keyboard input.

## Fix

Handle Escape explicitly through document.exitFullscreen and restore focus to the initiating
button; fullscreenchange synchronizes aria-expanded. Tab edge trapping also covers expanded
fallback. No inline script/style or browser sandbox changes.

## Regression

Persistent prototype browser-check verifies fullscreen → Escape, aria state and focus return.
STEP-0026 evidence records real browser rerun; no inferred PASS from source alone.
