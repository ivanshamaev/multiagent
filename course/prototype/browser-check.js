async page => {
  const base = "http://127.0.0.1:8099/course/";
  const artifacts = "output/playwright/step28/";
  const errors = [], failed = [], external = [];
  page.on("pageerror", error => errors.push(error.message));
  page.on("console", message => { if (message.type() === "error") errors.push(message.text()); });
  page.on("requestfailed", request => failed.push(request.url()));
  page.on("request", request => { if (!request.url().startsWith(base)) external.push(request.url()); });
  const report = {};
  const check = (condition, name) => { if (!condition) throw new Error(name); };
  for (const file of ["prototype.html", "technical-requirements.html"]) {
    await page.goto(base + file);
    await page.evaluate(() => document.fonts.ready);
    report[file] = await page.evaluate(() => {
      const ids = Array.from(document.querySelectorAll("[id]"), e => e.id);
      const clipped = [];
      const svgs = Array.from(document.querySelectorAll("figure svg"));
      for (const svg of svgs) {
        const box = svg.viewBox.baseVal;
        for (const text of svg.querySelectorAll("text")) {
          if (!text.checkVisibility() || !text.getScreenCTM()) continue;
          const local = text.getBBox();
          if (!local.width || !local.height) continue;
          const transform = svg.getScreenCTM().inverse().multiply(text.getScreenCTM());
          const corners = [[local.x, local.y], [local.x + local.width, local.y],
            [local.x, local.y + local.height], [local.x + local.width, local.y + local.height]]
            .map(([x, y]) => ({ x: transform.a * x + transform.c * y + transform.e,
              y: transform.b * x + transform.d * y + transform.f }));
          if (corners.some(p => p.x < box.x - 4 || p.y < box.y - 4 || p.x > box.x + box.width + 4 || p.y > box.y + box.height + 4)) clipped.push(text.textContent);
        }
      }
      return { svgCount: svgs.length, uniqueIds: ids.length === new Set(ids).size,
        inlineStyles: document.querySelectorAll("[style]").length,
        inlineScripts: Array.from(document.scripts).filter(s => !s.src).length,
        accessible: svgs.every(s => s.querySelector("title") && s.querySelector("desc") && s.getAttribute("aria-labelledby")),
        noto: document.fonts.check('16px "Noto Sans"', "Теория"), clipped,
        pageOverflow: document.documentElement.scrollWidth > innerWidth + 2 };
    });
    check(report[file].uniqueIds && report[file].accessible && report[file].noto, "IDs/accessibility/fonts");
    check(!report[file].inlineStyles && !report[file].inlineScripts, "inline CSP content");
    check(report[file].clipped.length === 0, "clipped labels: " + JSON.stringify(report[file].clipped));
    check(!report[file].pageOverflow, "page overflow " + file);
    await page.screenshot({ path: artifacts + (file === "prototype.html" ? "desktop.png" : "tool-loop.png"), fullPage: true });
  }
  await page.goto(base + "prototype.html");
  const first = page.locator("figure.diagram").first();
  const svg = first.locator("svg");
  const original = await svg.getAttribute("viewBox");
  await first.locator('[data-action="zoom-in"]').click();
  check(await first.locator("output").textContent() === "125%", "zoom");
  check(await page.locator("figure.diagram").nth(1).locator("output").textContent() === "100%", "independent viewer state");
  await first.locator(".canvas").focus();
  await page.keyboard.press("ArrowRight");
  check(await svg.getAttribute("viewBox") !== original, "keyboard pan");
  await page.keyboard.press("0");
  check(await svg.getAttribute("viewBox") === original, "keyboard reset");
  await first.locator('[data-action="wheel"]').click();
  await first.locator(".canvas").hover();
  await page.mouse.wheel(0, -100);
  await page.waitForFunction(() => document.querySelector("figure output").textContent === "110%");
  await first.locator('[data-action="wheel"]').click();
  await first.locator('[data-action="reset"]').click();
  await first.locator('[data-action="pan"]').click();
  await first.locator(".canvas").scrollIntoViewIfNeeded();
  const area = await first.locator(".canvas").boundingBox();
  await page.mouse.move(area.x + 100, area.y + 80);
  await page.mouse.down();
  await page.mouse.move(area.x + 160, area.y + 100, { steps: 5 });
  await page.mouse.up();
  check(await svg.getAttribute("viewBox") !== original, "pointer pan");
  await first.locator('[data-action="pan"]').click();
  await first.locator('[data-action="reset"]').click();
  await first.locator('[data-action="fullscreen"]').click();
  check(await first.locator('[data-action="fullscreen"]').getAttribute("aria-expanded") === "true", "fullscreen entered");
  await page.keyboard.press("Escape");
  await page.waitForFunction(() => !document.fullscreenElement && !document.querySelector(".diagram.expanded"));
  check(await first.locator('[data-action="fullscreen"]').getAttribute("aria-expanded") === "false", "fullscreen exited");
  check(await first.locator('[data-action="fullscreen"]').evaluate(e => e === document.activeElement), "fullscreen focus return");
  await first.evaluate(e => { e.requestFullscreen = () => Promise.reject(new Error("fixture: unavailable")); });
  await first.locator('[data-action="fullscreen"]').click();
  await page.waitForFunction(() => Boolean(document.querySelector(".diagram.expanded")));
  await first.locator("a[href]").last().focus();
  await page.keyboard.press("Tab");
  check(await first.locator("button").first().evaluate(e => e === document.activeElement), "fullscreen tab cycle");
  await page.keyboard.press("Escape");
  check(await first.locator('[data-action="fullscreen"]').evaluate(e => e === document.activeElement), "fallback focus return");
  report.controls = "zoom/independence/wheel/pointer/keyboard/reset/fullscreen/fallback/Escape/focus PASS";
  await page.emulateMedia({ colorScheme: "dark", reducedMotion: "reduce" });
  report.dark = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  await page.screenshot({ path: artifacts + "dark.png", fullPage: true });
  await page.emulateMedia({ colorScheme: "light", reducedMotion: "no-preference" });
  await page.setViewportSize({ width: 360, height: 800 });
  await page.goto(base + "prototype.html");
  report.mobile = await page.evaluate(() => ({ overflow: document.documentElement.scrollWidth > innerWidth + 2,
    localScroll: document.querySelector(".canvas").scrollWidth > document.querySelector(".canvas").clientWidth }));
  check(!report.mobile.overflow && report.mobile.localScroll, "mobile overflow/local scroll");
  await page.screenshot({ path: artifacts + "mobile.png", fullPage: true });
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.goto(base + "prototype.html");
  await page.locator('[data-action="zoom-in"]').first().click();
  await page.evaluate(() => window.addEventListener("beforeprint", () => {
    window.printBoxesValid = Array.from(document.querySelectorAll("figure svg"))
      .every(s => s.getAttribute("viewBox") === s.dataset.originalViewbox.split(/[ ,]+/).map(Number).join(" "));
  }));
  await page.pdf({ path: artifacts + "print.pdf", printBackground: true });
  check(await page.evaluate(() => window.printBoxesValid), "full diagrams during print");
  check(await page.locator("figure").first().locator("output").textContent() === "125%", "post-print zoom state");
  await page.emulateMedia({ media: "print" });
  report.print = await page.evaluate(() => ({ controlsHidden: getComputedStyle(document.querySelector(".controls")).display === "none",
    overflow: getComputedStyle(document.querySelector(".canvas")).overflow }));
  check(report.print.controlsHidden && report.print.overflow === "visible", "print CSS");
  await page.emulateMedia({ media: "screen" });
  const noJsContext = await page.context().browser().newContext({ javaScriptEnabled: false, viewport: { width: 1280, height: 900 } });
  const noJs = await noJsContext.newPage();
  await noJs.goto(base + "prototype.html");
  report.noJs = await noJs.evaluate(() => ({ svgCount: document.querySelectorAll("figure svg").length,
    controlsHidden: getComputedStyle(document.querySelector(".controls")).display === "none",
    enhanced: Boolean(document.querySelector(".enhanced")) }));
  check(report.noJs.svgCount === 3 && report.noJs.controlsHidden && !report.noJs.enhanced, "no-JS fallback");
  await noJs.screenshot({ path: artifacts + "no-js.png", fullPage: true });
  await noJsContext.close();
  const touchContext = await page.context().browser().newContext({ hasTouch: true, viewport: { width: 360, height: 800 } });
  const touchPage = await touchContext.newPage();
  await touchPage.goto(base + "prototype.html");
  await touchPage.locator('[data-action="pan"]').first().click();
  const touchCanvas = touchPage.locator(".canvas").first();
  await touchCanvas.scrollIntoViewIfNeeded();
  const touchBox = await touchCanvas.boundingBox();
  const touchSvg = touchCanvas.locator("svg");
  const touchOriginal = await touchSvg.getAttribute("viewBox");
  const cdp = await touchContext.newCDPSession(touchPage);
  const point = { x: touchBox.x + 100, y: touchBox.y + 80 };
  await cdp.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [point] });
  await cdp.send("Input.dispatchTouchEvent", { type: "touchMove", touchPoints: [{ x: point.x + 50, y: point.y + 20 }] });
  await cdp.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
  check(await touchSvg.getAttribute("viewBox") !== touchOriginal, "emulated touch pan");
  report.touch = "Chromium CDP emulation PASS (not hardware audit)";
  await touchContext.close();
  const response = await page.request.get(base);
  check(response.status() === 200 && !response.headers()["content-security-policy"].includes("unsafe-inline"), "served CSP/subpath");
  check((await page.request.get(base + "../.env")).status() === 404, "preview boundary");
  report.errors = errors; report.failedRequests = failed; report.externalRequests = external;
  check(!errors.length && !failed.length && !external.length, "console/network/CSP errors");
  return report;
}
