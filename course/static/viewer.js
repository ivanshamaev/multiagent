"use strict";

const courseDisclosure = document.querySelector(".course-sidebar details");
if (courseDisclosure) {
  const wide = matchMedia("(min-width: 768px)");
  courseDisclosure.open = wide.matches;
  wide.addEventListener("change", event => { courseDisclosure.open = event.matches; });
}
const tocLinks = Array.from(document.querySelectorAll('.lecture-sidebar a[href^="#"], .mobile-toc a[href^="#"]'));
const headings = Array.from(document.querySelectorAll("article h2[id], article h3[id]"));
function markSection() {
  const active = headings.filter(h => h.getBoundingClientRect().top <= 120).pop() || headings[0];
  if (!active) return;
  for (const link of tocLinks) {
    if (decodeURIComponent(link.hash.slice(1)) === active.id) link.setAttribute("aria-current", "location");
    else link.removeAttribute("aria-current");
  }
}
if (headings.length) { window.addEventListener("scroll", markSection, { passive: true }); markSection(); }

const states = [];
for (const figure of document.querySelectorAll("figure.diagram")) {
  const svg = figure.querySelector("svg");
  const canvas = figure.querySelector(".canvas");
  const controls = figure.querySelector(".controls");
  const output = controls.querySelector("output");
  const original = svg.dataset.originalViewbox.split(/[ ,]+/).map(Number);
  const state = { figure, svg, canvas, controls, original, scale: 1, x: original[0], y: original[1], wheel: false, pan: false, drag: null };
  states.push(state);
  controls.hidden = false;
  figure.classList.add("enhanced");
  const fullscreenButton = controls.querySelector('[data-action="fullscreen"]');
  fullscreenButton.setAttribute("aria-expanded", "false");

  function apply() {
    state.x = Math.max(-2 * original[2], Math.min(2 * original[2], state.x));
    state.y = Math.max(-2 * original[3], Math.min(2 * original[3], state.y));
    svg.setAttribute("viewBox", [state.x, state.y, original[2] / state.scale, original[3] / state.scale].join(" "));
    output.textContent = `${Math.round(state.scale * 100)}%`;
  }
  function zoom(factor) {
    const next = Math.max(.5, Math.min(4, state.scale * factor));
    state.x += original[2] / (2 * state.scale) - original[2] / (2 * next);
    state.y += original[3] / (2 * state.scale) - original[3] / (2 * next);
    state.scale = next;
    apply();
  }
  function reset() {
    state.scale = 1; state.x = original[0]; state.y = original[1];
    canvas.scrollLeft = 0; canvas.scrollTop = 0; apply();
  }
  async function toggleFullscreen() {
    if (document.fullscreenElement === figure) {
      await document.exitFullscreen();
    } else if (figure.classList.contains("expanded")) {
      figure.classList.remove("expanded");
      fullscreenButton.setAttribute("aria-expanded", "false");
      fullscreenButton.focus();
    } else {
      try { await figure.requestFullscreen(); }
      catch (_) { figure.classList.add("expanded"); }
      fullscreenButton.setAttribute("aria-expanded", "true");
      fullscreenButton.focus();
    }
  }
  controls.addEventListener("click", (event) => {
    const button = event.target.closest("button");
    if (!button) return;
    const action = button.dataset.action;
    if (action === "zoom-in") zoom(1.25);
    if (action === "zoom-out") zoom(.8);
    if (action === "reset") reset();
    if (action === "fullscreen") toggleFullscreen();
    if (action === "wheel") {
      state.wheel = !state.wheel;
      button.setAttribute("aria-pressed", String(state.wheel));
    }
    if (action === "pan") {
      state.pan = !state.pan;
      button.setAttribute("aria-pressed", String(state.pan));
      canvas.classList.toggle("panning", state.pan);
    }
  });
  canvas.addEventListener("wheel", (event) => {
    if (!state.wheel) return;
    event.preventDefault(); zoom(event.deltaY < 0 ? 1.1 : 1 / 1.1);
  }, { passive: false });
  canvas.addEventListener("keydown", (event) => {
    const key = event.key;
    if (["+", "=", "-", "0", "Home", "ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(key)) event.preventDefault();
    if (key === "+" || key === "=") zoom(1.25);
    if (key === "-") zoom(.8);
    if (key === "0" || key === "Home") reset();
    if (key === "ArrowLeft") state.x -= original[2] / state.scale * .05;
    if (key === "ArrowRight") state.x += original[2] / state.scale * .05;
    if (key === "ArrowUp") state.y -= original[3] / state.scale * .05;
    if (key === "ArrowDown") state.y += original[3] / state.scale * .05;
    apply();
  });
  canvas.addEventListener("pointerdown", (event) => {
    if (!state.pan || event.button !== 0) return;
    event.preventDefault();
    canvas.focus(); canvas.setPointerCapture(event.pointerId);
    state.drag = { px: event.clientX, py: event.clientY, x: state.x, y: state.y };
    canvas.classList.add("dragging");
  });
  canvas.addEventListener("pointermove", (event) => {
    if (!state.drag) return;
    const rect = svg.getBoundingClientRect();
    state.x = state.drag.x - (event.clientX - state.drag.px) * original[2] / state.scale / rect.width;
    state.y = state.drag.y - (event.clientY - state.drag.py) * original[3] / state.scale / rect.height;
    apply();
  });
  function stopDrag() { state.drag = null; canvas.classList.remove("dragging"); }
  canvas.addEventListener("pointerup", stopDrag);
  canvas.addEventListener("pointercancel", stopDrag);
  canvas.addEventListener("lostpointercapture", stopDrag);
  document.addEventListener("fullscreenchange", () => {
    const active = document.fullscreenElement === figure;
    fullscreenButton.setAttribute("aria-expanded", String(active || figure.classList.contains("expanded")));
    if (!active && document.activeElement === document.body) fullscreenButton.focus();
  });
}
document.addEventListener("keydown", (event) => {
  if (event.key === "Tab") {
    const active = document.fullscreenElement || document.querySelector(".diagram.expanded");
    if (active) {
      const focusable = Array.from(active.querySelectorAll("button, [tabindex], a[href]"));
      const target = event.shiftKey ? focusable[focusable.length - 1] : focusable[0];
      const edge = event.shiftKey ? focusable[0] : focusable[focusable.length - 1];
      if (document.activeElement === edge) { event.preventDefault(); target.focus(); }
    }
  }
  if (event.key !== "Escape") return;
  if (document.fullscreenElement) {
    const button = document.fullscreenElement.querySelector('[data-action="fullscreen"]');
    document.exitFullscreen().then(() => button.focus());
  }
  for (const state of states) {
    if (state.figure.classList.contains("expanded")) {
      state.figure.classList.remove("expanded");
      const button = state.controls.querySelector('[data-action="fullscreen"]');
      button.setAttribute("aria-expanded", "false"); button.focus();
    }
  }
});
let printStates = [];
window.addEventListener("beforeprint", () => {
  printStates = states.map(s => s.svg.getAttribute("viewBox"));
  states.forEach(s => s.svg.setAttribute("viewBox", s.original.join(" ")));
});
window.addEventListener("afterprint", () => states.forEach((s, i) => s.svg.setAttribute("viewBox", printStates[i])));
