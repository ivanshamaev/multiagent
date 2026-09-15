async page => {
  const base = "http://127.0.0.1:8099/course/";
  const artifacts = "output/playwright/step28/";
  const errors = [], external = [];
  page.on("pageerror", e => errors.push(e.message));
  page.on("console", e => { if (e.type() === "error") errors.push(e.text()); });
  page.on("request", r => { if (!r.url().startsWith(base)) external.push(r.url()); });
  const check = (value, message) => { if (!value) throw new Error(message); };
  const report = {};
  await page.setViewportSize({ width: 1600, height: 1000 });
  await page.goto(base);
  await page.evaluate(() => document.fonts.ready);
  check(await page.locator("#roadmap-svg a").count() === 27, "roadmap links");
  check(await page.locator(".topic-card").count() === 27, "catalog");
  await page.screenshot({ path: artifacts + "landing-desktop.png" });
  await page.locator("#roadmap").scrollIntoViewIfNeeded();
  await page.screenshot({ path: artifacts + "roadmap.png" });
  await page.locator("#roadmap-svg a").first().click();
  check(page.url().endsWith("topic-0000.html"), "SVG navigation");
  check(await page.locator(".course-sidebar details").getAttribute("open") !== null, "desktop course open");
  check(await page.locator(".lecture-sidebar").isVisible(), "desktop right TOC");
  check(await page.locator("article .status").textContent().then(s => s.includes("не написан")), "honest status");
  await page.screenshot({ path: artifacts + "reader-desktop.png", fullPage: true });
  const selectedSection = await page.locator(".lecture-sidebar a").nth(2).getAttribute("href");
  await page.locator(".lecture-sidebar a").nth(2).click();
  await page.waitForFunction(anchor => document.querySelector('.lecture-sidebar a[aria-current="location"]')?.getAttribute("href") === anchor, selectedSection);
  report.desktop = "landing/SVG navigation/course sidebar/AST TOC/outline status PASS";
  for (const width of [360, 768, 1280, 1600]) {
    await page.setViewportSize({ width, height: 900 });
    for (const file of ["index.html", "topic-0000.html", "topic-0026.html", "prototype.html", "technical-requirements.html"]) {
      await page.goto(base + file);
      const state = await page.evaluate(() => {
        const ids = Array.from(document.querySelectorAll("[id]"), e => e.id);
        return { overflow: document.documentElement.scrollWidth > innerWidth + 2,
          duplicateIds: ids.length !== new Set(ids).size,
          inline: document.querySelectorAll("[style],script:not([src])").length };
      });
      check(!state.overflow && !state.duplicateIds && !state.inline, "responsive/IDs/CSP " + width + "/" + file);
    }
  }
  await page.setViewportSize({ width: 360, height: 800 });
  await page.goto(base + "topic-0000.html");
  check(await page.locator(".course-sidebar details").getAttribute("open") === null, "mobile course collapsed");
  check(await page.locator(".mobile-toc").isVisible(), "mobile TOC");
  await page.locator(".course-sidebar summary").click();
  check(await page.locator(".course-sidebar a").first().isVisible(), "mobile course disclosure");
  await page.locator(".course-sidebar summary").click();
  await page.locator(".mobile-toc summary").click();
  await page.locator(".mobile-toc a").first().click();
  await page.screenshot({ path: artifacts + "reader-mobile.png", fullPage: true });
  await page.goto(base);
  await page.screenshot({ path: artifacts + "landing-mobile.png" });
  await page.emulateMedia({ reducedMotion: "reduce" });
  check(await page.locator(".hero-title span").evaluate(e => getComputedStyle(e).animationName === "none"), "reduced motion");
  const noJs = await page.context().browser().newContext({ javaScriptEnabled: false, viewport: { width: 360, height: 800 } });
  const fallback = await noJs.newPage();
  await fallback.goto(base);
  check(await fallback.locator("#roadmap-svg a").count() === 27, "no-JS SVG");
  await fallback.locator(".roadmap-list summary").click();
  check(await fallback.locator(".roadmap-list a").first().isVisible(), "no-JS HTML roadmap");
  await fallback.goto(base + "topic-0000.html");
  await fallback.locator(".course-sidebar summary").click();
  check(await fallback.locator(".course-sidebar a").count() === 27, "no-JS course navigation");
  await fallback.screenshot({ path: artifacts + "no-js-reader.png" });
  await noJs.close();
  report.responsive = "360/768/1280/1600; disclosures/reduced-motion/no-JS PASS";
  check(!errors.length && !external.length, "console or external requests");
  report.errors = errors; report.externalRequests = external;
  return report;
}
