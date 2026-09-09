/* 강의별 위젯 등록 파일. 공통 shared.js는 수정하지 않습니다.
 * 등록: window.WIDGETS["이름"] = function (host, site) { ... };
 * HTML: <div data-widget="이름"><p>로드 실패 시에도 읽을 수 있는 정적 설명</p></div>
 * 아래 value-slider는 label + range + output을 연결한 범용 예시입니다.
 * 네이티브 range의 방향키/Home/End를 사용하며 발표 단축키와 충돌하지 않습니다.
 * 스타일은 lecture.css의 토큰 기반 클래스에 둡니다. 색상을 JS에 작성하지 않습니다.
 * factory는 동기 함수입니다. UI를 완성한 뒤 host.replaceChildren(...)으로 교체합니다.
 * 초기화 중 예외가 발생하면 원래 정적 설명을 복원합니다. 미등록 위젯도 설명을 유지합니다.
 * 새 요소는 window.mountWidgets(container)로 마운트합니다. 성공한 요소는 한 번만 초기화합니다.
 * site.levels로 강의 메타를 읽습니다. 단일 강의는 site.levels[0]입니다.
 */
window.WIDGETS = window.WIDGETS || {};

(function () {
  "use strict";
  let serial = 0;
  function node(tag, className, text) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (text !== undefined) el.textContent = text;
    return el;
  }

  window.WIDGETS["value-slider"] = function (host) {
    const panel = node("div", "interactive-widget value-slider");
    const heading = node("h3", "widget-title", "값 조절 예시");
    const label = node("label", "widget-slider", "값 (0–100)");
    const input = node("input");
    input.type = "range";
    input.id = "value-slider-" + (++serial);
    input.min = "0";
    input.max = "100";
    input.step = "1";
    input.value = "50";
    label.htmlFor = input.id;
    const output = node("output", "widget-result");
    output.htmlFor = input.id;
    output.setAttribute("aria-live", "polite");
    const meter = node("div", "widget-meter");
    meter.setAttribute("aria-hidden", "true");
    meter.append(node("span", "widget-meter-fill"));
    const note = node("p", "widget-note", "슬라이더를 움직이거나 방향키로 값을 조절하세요. Home은 0, End는 100입니다.");
    note.id = input.id + "-help";
    input.setAttribute("aria-describedby", note.id);
    function update() {
      const value = Number(input.value);
      output.textContent = "현재 값 " + value + " / 100";
      input.setAttribute("aria-valuetext", value + " / 100");
      panel.style.setProperty("--demo-value", String(value / 100));
    }
    input.addEventListener("input", update);
    input.addEventListener("change", update);
    panel.addEventListener("keydown", function (event) {
      if (["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "Home", "End", "PageUp", "PageDown"].includes(event.key)) event.stopPropagation();
    });
    panel.append(heading, label, input, output, meter, note);
    update();
    host.replaceChildren(panel);
  };


  // 주차 선택과 이전·다음은 ready 페이지에만 연결합니다.
  // coming 페이지를 직접 열었을 때 이전·다음은 비활성 상태입니다.
  window.WIDGETS["week-navigation"] = function (host, site) {
    const levels = Array.isArray(site.levels) ? site.levels : [];
    const slug = document.body.dataset.level;
    const current = levels.find(function (level) { return level.slug === slug; });
    if (!current) return;
    const ready = levels.filter(function (level) { return level.status === "ready"; });
    const currentIndex = ready.indexOf(current);
    const nav = node("nav", "week-navigation");
    nav.setAttribute("aria-label", "주차 이동");
    const form = node("form", "week-picker");
    const label = node("label", "week-picker-label", "주차 선택");
    const select = node("select", "week-select");
    select.id = "week-select-" + (++serial);
    label.htmlFor = select.id;
    levels.forEach(function (level) {
      const option = node("option", "", level.badge + " · " + level.title
        + (level.status === "ready" ? "" : " · 준비 중"));
      option.value = level.slug;
      option.disabled = level.status !== "ready";
      option.selected = level.slug === slug;
      select.append(option);
    });
    select.disabled = ready.length === 0;
    const go = node("button", "button", "이동");
    go.type = "submit";
    function selectedReady() {
      return ready.find(function (level) { return level.slug === select.value; });
    }
    function update() {
      go.disabled = !selectedReady() || select.value === slug;
    }
    select.addEventListener("change", update);
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      const target = selectedReady();
      if (target && target.slug !== slug) {
        window.location.assign("../" + encodeURIComponent(target.slug) + "/index.html");
      }
    });
    form.append(label, select, go);
    update();

    const steps = node("div", "week-steps");
    function step(level, label) {
      if (!level) {
        const disabled = node("button", "button", label);
        disabled.type = "button";
        disabled.disabled = true;
        return disabled;
      }
      const link = node("a", "button", label + " · " + level.badge);
      link.href = "../" + encodeURIComponent(level.slug) + "/index.html";
      link.setAttribute("aria-label", label + ": " + level.badge + " " + level.title);
      return link;
    }
    steps.append(
      step(currentIndex > 0 ? ready[currentIndex - 1] : undefined, "← 이전 주차"),
      step(currentIndex >= 0 ? ready[currentIndex + 1] : undefined, "다음 주차 →")
    );
    const status = node("p", "week-navigation-status", ready.length === 0
      ? "공개된 주차가 없습니다. 학습 자료는 주차별로 준비 중입니다."
      : current.status === "ready"
        ? "공개된 주차 사이에서 이동할 수 있습니다."
        : "이 주차는 준비 중입니다. 주차 선택에서 공개된 자료로 이동할 수 있습니다.");
    status.id = select.id + "-status";
    select.setAttribute("aria-describedby", status.id);
    nav.append(form, steps, status);
    host.replaceChildren(nav);
  };

  // 본문 바로가기는 공통 목차와 별도로 처리합니다.
  // 발표 모드는 원래 노드를 옮기므로 같은 링크의 상태를 바꾸고 종료 시 복원합니다.
  function initLessonAnchors() {
    const links = new Map();
    const panels = new Set();
    document.querySelectorAll('main a[href^="#"]').forEach(function (link) {
      const href = link.getAttribute("href");
      let id;
      try { id = decodeURIComponent(href.slice(1)); } catch (_) { return; }
      const target = id && document.getElementById(id);
      if (!target) return;
      const attributes = {};
      ["href", "tabindex", "role", "aria-disabled"].forEach(function (name) {
        attributes[name] = link.getAttribute(name);
      });
      links.set(link, { target, href, attributes });
      link.dataset.lessonAnchor = "";
      const panel = link.closest("[data-slide]");
      if (panel) panels.add(panel);
    });
    if (!links.size) return;
    panels.forEach(function (panel) {
      panel.append(node("p", "lesson-anchor-note", "이 바로가기는 일반 화면에서 사용할 수 있습니다. Esc로 발표를 종료한 뒤 선택하세요."));
    });
    let disabled = false;
    function setDisabled(value) {
      if (disabled === value) return;
      disabled = value;
      links.forEach(function (entry, link) {
        if (value) {
          link.removeAttribute("href");
          link.setAttribute("role", "link");
          link.setAttribute("aria-disabled", "true");
          link.setAttribute("tabindex", "-1");
        } else {
          Object.keys(entry.attributes).forEach(function (name) {
            const original = entry.attributes[name];
            if (original === null) link.removeAttribute(name);
            else link.setAttribute(name, original);
          });
        }
      });
    }
    document.addEventListener("click", function (event) {
      if (!(event.target instanceof Element)) return;
      const link = event.target.closest("a[data-lesson-anchor]");
      const entry = links.get(link);
      if (!entry) return;
      if (disabled || document.body.classList.contains("is-presenting")) {
        event.preventDefault();
        return;
      }
      if (event.defaultPrevented || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      if (window.location.hash !== entry.href) {
        try { window.history.pushState(null, "", entry.href); }
        catch (_) { window.location.hash = entry.href; }
      }
      if (!entry.target.hasAttribute("tabindex")) entry.target.setAttribute("tabindex", "-1");
      entry.target.focus({ preventScroll: true });
      entry.target.scrollIntoView({ block: "start", behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
    });
    document.addEventListener("lecture:presentation-enter", function () { setDisabled(true); });
    // 공통 구현에 종료 이벤트가 없어 body의 발표 상태 클래스로 복원합니다.
    const sync = function () { setDisabled(document.body.classList.contains("is-presenting")); };
    new MutationObserver(sync).observe(document.body, { attributes: true, attributeFilter: ["class"] });
    sync();
  }

  const mounted = new WeakSet();
  function mountWidgets(root = document) {
    const elements = Array.from(root.querySelectorAll("[data-widget]"));
    if (root instanceof Element && root.matches("[data-widget]")) elements.unshift(root);
    elements.forEach(function (host) {
      if (mounted.has(host) || host.closest("[hidden]")) return;
      const name = host.dataset.widget;
      const factory = Object.prototype.hasOwnProperty.call(window.WIDGETS, name) ? window.WIDGETS[name] : undefined;
      if (typeof factory !== "function") return;
      const fallback = Array.from(host.childNodes);
      try {
        factory(host, window.SITE || {});
        mounted.add(host);
        host.dataset.widgetReady = "true";
      } catch (_) {
        host.replaceChildren.apply(host, fallback);
        host.dataset.widgetReady = "false";
      }
    });
  }
  window.mountWidgets = mountWidgets;
  function init() {
    mountWidgets();
    initLessonAnchors();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();
