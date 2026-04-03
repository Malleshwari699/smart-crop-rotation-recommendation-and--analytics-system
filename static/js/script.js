/* =============================================================================
   script.js — Smart Crop Recommendation System
   Rich Animations · Floating Leaves · Parallax · Counters · Interactions
   ============================================================================= */
"use strict";

const $ = (s, c = document) => c.querySelector(s);
const $$ = (s, c = document) => [...c.querySelectorAll(s)];
const on = (el, ev, fn) => el && el.addEventListener(ev, fn);

/* ══════════════════════════════════════════════════════════════════
   1. PAGE ENTRANCE — smooth fade-in
   ══════════════════════════════════════════════════════════════════ */
document.documentElement.style.opacity = "0";
document.documentElement.style.transition = "opacity 0.5s ease";
window.addEventListener("load", () => {
  document.documentElement.style.opacity = "1";
});

/* ══════════════════════════════════════════════════════════════════
   2. FLOATING LEAF PARTICLES
   ══════════════════════════════════════════════════════════════════ */
(function spawnLeaves() {
  const LEAVES = ["🍃","🌿","🌱","🍀","🌾","🌲"];
  const COUNT  = window.innerWidth < 600 ? 10 : 22;

  for (let i = 0; i < COUNT; i++) {
    const el = document.createElement("span");
    el.className = "leaf-particle";
    el.textContent = LEAVES[Math.floor(Math.random() * LEAVES.length)];

    const size     = 0.75 + Math.random() * 1.4;
    const duration = 9 + Math.random() * 16;
    const delay    = Math.random() * -18;
    const leftPct  = Math.random() * 105;

    el.style.cssText = `
      left: ${leftPct}vw;
      font-size: ${size}rem;
      animation-duration: ${duration}s;
      animation-delay: ${delay}s;
      opacity: ${0.12 + Math.random() * 0.22};
    `;
    document.body.appendChild(el);
  }
})();

/* ══════════════════════════════════════════════════════════════════
   3. NAVBAR — hamburger + active link underline
   ══════════════════════════════════════════════════════════════════ */
(function initNavbar() {
  const hamburger = $(".hamburger");
  const navLinks  = $(".nav-links");
  if (!hamburger || !navLinks) return;

  on(hamburger, "click", () => {
    const open = navLinks.classList.toggle("open");
    const [s1,,s3] = $$("span", hamburger);
    hamburger.querySelector("span:nth-child(1)").style.transform = open ? "rotate(45deg) translate(5px,5px)"  : "";
    hamburger.querySelector("span:nth-child(2)").style.opacity   = open ? "0" : "";
    hamburger.querySelector("span:nth-child(3)").style.transform = open ? "rotate(-45deg) translate(5px,-5px)" : "";
  });

  // Close on outside click
  on(document, "click", e => {
    if (!navLinks.contains(e.target) && !hamburger.contains(e.target))
      navLinks.classList.remove("open");
  });

  // Active state
  const path = window.location.pathname;
  $$(".nav-links a").forEach(a => {
    const href = a.getAttribute("href");
    if (href === path || (href !== "/" && path.startsWith(href)))
      a.classList.add("active");
  });
})();

/* ══════════════════════════════════════════════════════════════════
   4. LANGUAGE SWITCHER
   ══════════════════════════════════════════════════════════════════ */
(function initLang() {
  const sel = $(".lang-select");
  if (!sel) return;
  const saved = localStorage.getItem("cropLang");
  if (saved) sel.value = saved;
  on(sel, "change", () => {
    localStorage.setItem("cropLang", sel.value);
    fetch("/set_lang", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lang: sel.value })
    }).then(() => window.location.reload());
  });
})();

/* ══════════════════════════════════════════════════════════════════
   5. SCROLL REVEAL  (IntersectionObserver)
   ══════════════════════════════════════════════════════════════════ */
(function initReveal() {
  // Auto-tag common elements if not already tagged
  $$(".feature-card, .metric-card, .chart-card, .result-card, .card, .login-card")
    .forEach((el, i) => {
      if (!el.classList.contains("reveal") &&
          !el.classList.contains("reveal-left") &&
          !el.classList.contains("reveal-scale")) {
        el.classList.add("reveal");
        el.style.transitionDelay = `${i * 0.06}s`;
      }
    });

  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add("visible");
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.1, rootMargin: "0px 0px -40px 0px" });

  $$(".reveal, .reveal-left, .reveal-right, .reveal-scale").forEach(el => obs.observe(el));
})();

/* ══════════════════════════════════════════════════════════════════
   6. ANIMATED COUNTERS
   ══════════════════════════════════════════════════════════════════ */
function animateCounter(el, target, suffix, duration = 1400) {
  const t0 = performance.now();
  const isFloat = String(target).includes(".");
  const digits  = isFloat ? 2 : 0;

  function step(now) {
    const p = Math.min((now - t0) / duration, 1);
    const ease = 1 - Math.pow(1 - p, 3);
    el.textContent = (target * ease).toFixed(digits) + suffix;
    if (p < 1) requestAnimationFrame(step);
    else el.textContent = target.toFixed(digits) + suffix;
  }
  requestAnimationFrame(step);
}

(function initCounters() {
  const els = $$("[data-count]");
  if (!els.length) return;
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        animateCounter(
          e.target,
          parseFloat(e.target.dataset.count),
          e.target.dataset.suffix || "",
          1300
        );
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.5 });
  els.forEach(el => obs.observe(el));
})();

/* ══════════════════════════════════════════════════════════════════
   7. HERO PARALLAX on mouse move
   ══════════════════════════════════════════════════════════════════ */
(function initParallax() {
  const hero = $(".hero");
  if (!hero) return;
  on(hero, "mousemove", e => {
    const cx = hero.clientWidth  / 2;
    const cy = hero.clientHeight / 2;
    const dx = (e.clientX - cx) / cx;
    const dy = (e.clientY - cy) / cy;
    const content = $(".hero-content", hero);
    if (content) {
      content.style.transform = `translate(${dx * 6}px, ${dy * 4}px)`;
    }
  });
  on(hero, "mouseleave", () => {
    const content = $(".hero-content", hero);
    if (content) content.style.transform = "translate(0,0)";
  });
})();

/* ══════════════════════════════════════════════════════════════════
   8. PREDICTION FORM — sliders + validation + loader
   ══════════════════════════════════════════════════════════════════ */
(function initPredictionForm() {
  const form   = $("#prediction-form");
  const loader = $(".loader-overlay");
  if (!form) return;

  // Live range-slider display
  $$(".range-input", form).forEach(inp => {
    const disp = $(`#${inp.id}-val`);
    if (!disp) return;
    const fmt = () => {
      disp.textContent = parseFloat(inp.value).toFixed(
        inp.step && inp.step.includes(".") ? 2 : 0
      );
    };
    on(inp, "input", fmt);
    fmt();
  });

  // Submit
  on(form, "submit", e => {
    let ok = true;
    $$("input[required], select[required]", form).forEach(inp => {
      if (!inp.value.trim()) { inp.style.borderColor = "#E53935"; ok = false; }
    });
    if (!ok) { e.preventDefault(); showFlash("Please fill in all required fields.", "danger"); return; }
    if (loader) loader.classList.add("active");
  });

  // Reset
  const resetBtn = $("#reset-btn");
  on(resetBtn, "click", () => {
    form.reset();
    $$(".range-input", form).forEach(inp => {
      const d = $(`#${inp.id}-val`);
      if (d) d.textContent = parseFloat(inp.value).toFixed(inp.step?.includes(".") ? 2 : 0);
      inp.style.borderColor = "";
    });
  });
})();

/* ══════════════════════════════════════════════════════════════════
   9. TOP-5 PROBABILITY BARS — animate on load
   ══════════════════════════════════════════════════════════════════ */
(function initTop5() {
  $$(".top5-bar-inner").forEach((bar, i) => {
    const target = bar.dataset.width || bar.style.width;
    bar.style.width = "0";
    setTimeout(() => { bar.style.width = target; }, 300 + i * 100);
  });
})();

/* ══════════════════════════════════════════════════════════════════
   10. PERFORMANCE METRIC BARS — animate when visible
   ══════════════════════════════════════════════════════════════════ */
(function initPerfBars() {
  const bars = $$(".perf-bar-inner");
  if (!bars.length) return;
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        const bar = e.target;
        const w   = bar.dataset.width || "0%";
        bar.style.width = "0";
        setTimeout(() => { bar.style.width = w; }, 150);
        obs.unobserve(bar);
      }
    });
  }, { threshold: 0.3 });
  bars.forEach(b => { b.style.width = "0"; obs.observe(b); });
})();

/* ══════════════════════════════════════════════════════════════════
   11. TAB SWITCHER
   ══════════════════════════════════════════════════════════════════ */
(function initTabs() {
  $$(".tab-switcher").forEach(sw => {
    const btns = $$(".tab-btn", sw);
    const panels = $$(".tab-panel");
    on(sw, "click", e => {
      const btn = e.target.closest(".tab-btn");
      if (!btn) return;
      btns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      panels.forEach(p => {
        const show = p.dataset.tab === btn.dataset.tab;
        p.style.display = show ? "" : "none";
        if (show) {
          p.style.animation = "fadeInUp 0.4s ease both";
          // Re-trigger bar animations inside this tab
          $$(".perf-bar-inner", p).forEach(b => {
            const w = b.dataset.width || b.style.width;
            b.style.width = "0";
            setTimeout(() => { b.style.width = w; }, 100);
          });
        }
      });
    });
    if (btns[0]) btns[0].click();
  });
})();

/* ══════════════════════════════════════════════════════════════════
   12. FLASH / TOAST NOTIFICATIONS
   ══════════════════════════════════════════════════════════════════ */
function showFlash(msg, type = "info", duration = 4200) {
  let container = $("#flash-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "flash-container";
    container.style.cssText = "position:fixed;top:80px;right:1.2rem;z-index:8000;min-width:280px;max-width:380px;";
    document.body.appendChild(container);
  }
  const icons = { danger:"⚠️", success:"✅", info:"ℹ️" };
  const div = document.createElement("div");
  div.className = `alert alert-${type}`;
  div.style.cssText = "cursor:pointer;margin-bottom:0.6rem;box-shadow:0 6px 24px rgba(0,0,0,0.15);";
  div.innerHTML = `<span>${icons[type]||"ℹ️"}</span> ${msg}`;
  on(div, "click", () => dismiss(div));
  container.appendChild(div);
  setTimeout(() => dismiss(div), duration);
}
function dismiss(el) {
  el.style.transition = "opacity 0.4s, transform 0.4s";
  el.style.opacity = "0"; el.style.transform = "translateX(110%)";
  setTimeout(() => el.remove(), 420);
}

// Auto-show server flash messages
$$(".server-flash").forEach(el => {
  showFlash(el.textContent.trim(), el.dataset.type || "info");
  el.remove();
});

/* ══════════════════════════════════════════════════════════════════
   13. LOGIN — password toggle + validation
   ══════════════════════════════════════════════════════════════════ */
(function initLogin() {
  const pwd    = $("#password");
  const toggle = $("#toggle-pwd");
  const form   = $("#login-form");
  const loader = $(".loader-overlay");

  on(toggle, "click", () => {
    const show = pwd.type === "password";
    pwd.type = show ? "text" : "password";
    toggle.textContent = show ? "🙈" : "👁";
  });

  on(form, "submit", e => {
    const u = $("#username"), p = $("#password");
    let ok = true;
    [u, p].forEach(inp => {
      if (!inp?.value.trim()) { if (inp) inp.style.borderColor = "#E53935"; ok = false; }
      else if (inp) inp.style.borderColor = "";
    });
    if (!ok) { e.preventDefault(); showFlash("Enter both username and password.", "danger"); return; }
    if (loader) loader.classList.add("active");
  });
})();

/* ══════════════════════════════════════════════════════════════════
   14. CHART LIGHTBOX — click any chart image to expand
   ══════════════════════════════════════════════════════════════════ */
(function initLightbox() {
  const charts = $$(".chart-img");
  if (!charts.length) return;

  const overlay = document.createElement("div");
  overlay.id = "lightbox";
  overlay.style.cssText = `
    position:fixed;inset:0;
    background:rgba(5,20,5,0.93);
    backdrop-filter:blur(8px);
    display:flex;align-items:center;justify-content:center;
    z-index:9999;opacity:0;pointer-events:none;
    transition:opacity 0.35s;cursor:zoom-out;padding:1rem;
  `;
  const img = document.createElement("img");
  img.style.cssText = "max-width:95vw;max-height:92vh;border-radius:14px;box-shadow:0 24px 70px rgba(0,0,0,0.6);transform:scale(0.9);transition:transform 0.35s cubic-bezier(0.34,1.56,0.64,1);";
  overlay.appendChild(img);
  document.body.appendChild(overlay);

  charts.forEach(c => {
    on(c, "click", () => {
      img.src = c.src;
      overlay.style.opacity = "1"; overlay.style.pointerEvents = "all";
      setTimeout(() => img.style.transform = "scale(1)", 10);
    });
  });
  on(overlay, "click", () => {
    overlay.style.opacity = "0"; overlay.style.pointerEvents = "none";
    img.style.transform = "scale(0.9)";
  });
  on(document, "keydown", e => {
    if (e.key === "Escape") { overlay.style.opacity = "0"; overlay.style.pointerEvents = "none"; }
  });
})();

/* ══════════════════════════════════════════════════════════════════
   15. HOVER TILT on cards (subtle 3D)
   ══════════════════════════════════════════════════════════════════ */
(function initTilt() {
  $$(".metric-card, .feature-card").forEach(card => {
    on(card, "mousemove", e => {
      const r = card.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width  - 0.5;
      const y = (e.clientY - r.top)  / r.height - 0.5;
      card.style.transform = `translateY(-6px) rotateY(${x*10}deg) rotateX(${-y*8}deg)`;
    });
    on(card, "mouseleave", () => {
      card.style.transform = "";
      card.style.transition = "transform 0.5s ease";
    });
    on(card, "mouseenter", () => {
      card.style.transition = "transform 0.12s ease";
    });
  });
})();

/* ══════════════════════════════════════════════════════════════════
   16. SMOOTH SCROLL for anchor links
   ══════════════════════════════════════════════════════════════════ */
$$('a[href^="#"]').forEach(a => {
  on(a, "click", e => {
    const t = $(a.getAttribute("href"));
    if (t) { e.preventDefault(); t.scrollIntoView({ behavior: "smooth", block: "start" }); }
  });
});

/* ══════════════════════════════════════════════════════════════════
   17. RESULT HERO SHINE ELEMENT
   ══════════════════════════════════════════════════════════════════ */
(function addResultShine() {
  const hero = $(".result-hero");
  if (!hero) return;
  const shine = document.createElement("div");
  shine.className = "shine";
  hero.insertBefore(shine, hero.firstChild);
})();

/* ══════════════════════════════════════════════════════════════════
   18. SCROLL PROGRESS BAR at top of page
   ══════════════════════════════════════════════════════════════════ */
(function initScrollProgress() {
  const bar = document.createElement("div");
  bar.style.cssText = `
    position:fixed;top:0;left:0;height:3px;width:0%;
    background:linear-gradient(90deg,#1B5E20,#66BB6A,#1B5E20);
    background-size:200% 100%;
    animation:gradientShift 3s ease infinite;
    z-index:9998;transition:width 0.1s linear;
    box-shadow:0 0 8px rgba(67,160,71,0.6);
  `;
  document.body.appendChild(bar);
  on(window, "scroll", () => {
    const h = document.documentElement;
    const pct = (h.scrollTop / (h.scrollHeight - h.clientHeight)) * 100;
    bar.style.width = pct + "%";
  });
})();

/* ══════════════════════════════════════════════════════════════════
   19. TYPING ANIMATION for hero title (optional enhancement)
   ══════════════════════════════════════════════════════════════════ */
(function initHeroTyping() {
  const badge = $(".hero-badge");
  if (!badge) return;
  // Add blinking cursor feel by toggling a border
  setInterval(() => {
    badge.style.borderColor = badge.style.borderColor === "rgba(255,255,255,0.6)"
      ? "rgba(255,255,255,0.25)"
      : "rgba(255,255,255,0.6)";
  }, 800);
})();

/* ══════════════════════════════════════════════════════════════════
   20. FORM INPUT FOCUS ANIMATIONS
   ══════════════════════════════════════════════════════════════════ */
(function initInputAnimations() {
  $$(".form-control, input[type='range']").forEach(inp => {
    on(inp, "focus", () => {
      const grp = inp.closest(".form-group");
      if (grp) grp.style.transform = "scale(1.01)";
    });
    on(inp, "blur", () => {
      const grp = inp.closest(".form-group");
      if (grp) grp.style.transform = "";
    });
  });
})();
