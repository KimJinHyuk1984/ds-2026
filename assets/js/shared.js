/* ★ 공통 자산: 템플릿 원본에서만 수정하고 sync-shared.sh 또는 sync-shared.ps1로 강의 저장소에 배포합니다.
 * 강의 정보는 data/site.js, 강의별 인터랙션은 widgets.js에서 변경합니다.
 * 외부 라이브러리·원격 데이터 요청·ES module 없이 HTTP와 file://에서 동일하게 실행합니다.
 */
(function () {
  "use strict";
  const site = window.SITE || {};
  const levels = Array.isArray(site.levels) ? site.levels : [];
  // data/site.js 기준으로 이미지 주소를 계산하므로 루트와 하위 강의가 함께 사용합니다.
  const dataScript = document.querySelector('script[src$="data/site.js"]');
  const siteRoot = dataScript ? new URL("../", dataScript.src) : new URL("./", document.baseURI);
  function assetURL(path) { return new URL(path, siteRoot).href; }
  function currentLevel() {
    // 단일 강의의 slug는 URL 라우팅에 쓰지 않습니다. 루트가 바로 강의입니다.
    if (levels.length === 1) return levels[0];
    const slug = document.body.dataset.level;
    return slug ? levels.find(function (level) { return level.slug === slug; }) : undefined;
  }
  const root = document.documentElement;
  const themeKey = "lecture-template-theme";
  const systemTheme = window.matchMedia("(prefers-color-scheme: dark)");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  let preferredTheme = null;
  try {
    const saved = localStorage.getItem(themeKey);
    if (saved === "light" || saved === "dark") preferredTheme = saved;
  } catch (_) { /* 저장소가 차단된 file://·비공개 모드에서도 동작합니다. */ }
  root.dataset.theme = preferredTheme || (systemTheme.matches ? "dark" : "light");

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = String(text);
    return node;
  }

  function fill(selector, value) {
    document.querySelectorAll(selector).forEach(function (node) {
      node.textContent = value == null ? "" : String(value);
    });
  }

  function applyLectureMeta() {
    const lecture = currentLevel();
    if (!lecture) return;
    const title = lecture.title || "강의 제목";
    document.title = title;
    fill("[data-lecture-title]", title);
    fill("[data-lecture-subtitle]", lecture.subtitle);
    fill("[data-lecture-kicker]", [lecture.emoji, lecture.kicker].filter(Boolean).join(" "));
    const description = document.querySelector('meta[name="description"]');
    if (description) description.content = lecture.subtitle || "";
    const brand = document.querySelector(".brand");
    if (brand) brand.setAttribute("aria-label", title + " 처음으로");
    document.body.dataset.accent = ["neon-green", "violet", "amber"].includes(lecture.accent)
      ? lecture.accent : "neon-green";
    const badges = document.querySelector("[data-lecture-badges]");
    if (!badges) return;
    badges.replaceChildren();
    [["레벨", levels.length > 1 ? lecture.badge : ""], ["난이도", lecture.difficulty], ["소요 시간", lecture.duration], ["대상", lecture.target]].forEach(function ([label, value]) {
      if (!value) return;
      const badge = element("span", "badge", value);
      badge.setAttribute("aria-label", label + ": " + value);
      badges.append(badge);
    });
    (Array.isArray(lecture.tags) ? lecture.tags : []).forEach(function (tag) {
      badges.append(element("span", "badge badge-tag", tag));
    });
  }

  function renderLevelCards() {
    const container = document.querySelector("[data-level-cards]");
    if (!container || levels.length < 2 || currentLevel()) return;
    const meta = site.site || {};
    document.title = meta.title || "";
    fill("[data-site-title]", meta.title);
    fill("[data-site-subtitle]", meta.subtitle);
    const description = document.querySelector('meta[name="description"]');
    if (description) description.content = meta.subtitle || "";
    container.replaceChildren();
    levels.forEach(function (level, index) {
      const item = element("li", "level-path-step");
      const number = element("span", "path-number", String(index + 1).padStart(2, "0"));
      number.setAttribute("aria-hidden", "true");
      const ready = level.status === "ready";
      const card = element(ready ? "a" : "article", "level-card");
      card.dataset.status = level.status;
      card.dataset.accent = level.accent;
      if (ready) card.setAttribute("href", "./" + encodeURIComponent(level.slug) + "/");
      else card.setAttribute("aria-disabled", "true");
      const content = element("div", "level-card-content");
      const top = element("div", "level-card-top");
      top.append(element("span", "kicker", [level.emoji, level.badge].filter(Boolean).join(" ")));
      if (!ready) top.append(element("span", "badge", "준비 중"));
      content.append(top, element("h3", "", level.title), element("p", "level-subtitle", level.subtitle));
      const details = element("div", "level-details");
      [level.difficulty, level.duration].filter(Boolean).forEach(function (value) {
        details.append(element("span", "badge", value));
      });
      const tags = element("div", "level-tags");
      (level.tags || []).forEach(function (tag) { tags.append(element("span", "badge badge-tag", tag)); });
      content.append(details, tags);
      if (ready) content.append(element("span", "level-cta", "강의 시작하기 →"));
      card.append(content);
      if (level.cover) {
        const cover = element("img", "level-cover");
        cover.src = assetURL(level.cover);
        cover.alt = level.title + " 강의 표지";
        cover.width = 1400;
        cover.height = 763;
        cover.loading = "lazy";
        cover.addEventListener("error", function () {
          cover.remove();
          card.classList.remove("has-cover");
        }, { once: true });
        card.append(cover);
        card.classList.add("has-cover");
      }
      item.append(number, card);
      container.append(item);
    });
  }

  function preparePage() {
    const lecture = currentLevel();
    const main = document.querySelector("main");
    if (!main) return;
    if (lecture) {
      document.body.dataset.page = "lecture";
      document.body.dataset.level = lecture.slug || "lecture";
      if (levels.length > 1 && !document.querySelector(".back-to-hub")) {
        const back = element("a", "back-to-hub", "← 강의 목록");
        back.href = assetURL("");
        const brand = document.querySelector(".brand");
        if (brand) brand.before(back);
      }
      return;
    }
    document.body.dataset.page = "hub";
    // 기존 루트의 예시 섹션을 숨기고 허브를 생성합니다. HTML의 별도 모드 설정은 없습니다.
    Array.from(main.children).forEach(function (child) { child.hidden = true; });
    document.querySelectorAll("[data-section-nav], [data-presentation-toggle], [data-progress]").forEach(function (node) { node.hidden = true; });
    const meta = site.site || {};
    fill("[data-lecture-title]", meta.title || "강의 목록");
    const brand = document.querySelector(".brand");
    if (brand) brand.setAttribute("aria-label", (meta.title || "강의 목록") + " 처음으로");
    const hub = element("div", "container");
    hub.dataset.hub = "";
    const hero = element("section", "hero");
    hero.id = "hub-top";
    if (brand) brand.href = "#hub-top";
    const heading = element("h1", "", meta.title || "강의 목록");
    heading.dataset.siteTitle = "";
    const subtitle = element("p", "hero-subtitle", meta.subtitle || "");
    subtitle.dataset.siteSubtitle = "";
    hero.append(heading, subtitle);
    const cards = element("ol", "level-path");
    cards.dataset.levelCards = "";
    cards.setAttribute("aria-label", "강의 목록");
    const profile = element("div", "hub-instructor");
    const avatar = element("div");
    avatar.dataset.instructorAvatar = "";
    const name = element("h2", "", ((site.instructor || {}).name || "") + " 선생님");
    const intro = element("button", "button button-primary", "선생님 소개 보기");
    intro.type = "button";
    intro.dataset.openInstructor = "";
    profile.append(avatar, name, intro);
    hub.append(hero, cards, profile);
    main.append(hub);
    if (!levels.length) cards.append(element("li", "", "등록된 강의가 없습니다."));
    renderLevelCards();
  }

  function makeAvatar(instructor, large = false) {
    const name = instructor.name || "선생님";
    const initials = /[가-힣]/.test(name) ? name.trim().slice(0, 1)
      : name.trim().split(/\s+/).map(function (part) { return part[0]; }).slice(0, 2).join("").toUpperCase();
    const avatar = element("div", "avatar" + (large ? " avatar-large" : ""), initials);
    avatar.setAttribute("role", "img");
    avatar.setAttribute("aria-label", name + " 이니셜 프로필");
    if (instructor.photo) {
      const photoPath = String(instructor.photo);
      if (!/^(?:[a-z]+:|\/|\\)/i.test(photoPath) && !photoPath.split(/[\/\\]/).includes("..")) {
        const image = element("img");
        image.alt = (instructor.name ? name + " 선생님" : name) + " 사진";
        image.loading = "lazy";
        image.width = large ? 80 : 56;
        image.height = large ? 80 : 56;
        image.addEventListener("load", function () {
          image.classList.add("is-loaded");
          avatar.removeAttribute("role");
          avatar.removeAttribute("aria-label");
        }, { once: true });
        image.addEventListener("error", function () { image.remove(); }, { once: true });
        image.src = assetURL(photoPath);
        avatar.append(image);
      }
    }
    return avatar;
  }

  function emailLink(node, email) {
    node.textContent = email || "";
    if (email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      node.setAttribute("href", "mailto:" + email);
    } else {
      node.removeAttribute("href");
    }
  }

  function renderInstructorModal() {
    const instructor = site.instructor || {};
    fill("[data-instructor-name]", instructor.name);
    fill("[data-instructor-affiliation]", instructor.affiliation);
    document.querySelectorAll("[data-instructor-email]").forEach(function (node) { emailLink(node, instructor.email); });
    document.querySelectorAll("[data-instructor-avatar]").forEach(function (node) { node.replaceChildren(makeAvatar(instructor)); });
    if (document.getElementById("instructor-dialog")) return;

    const dialog = element("dialog", "instructor-dialog");
    dialog.id = "instructor-dialog";
    dialog.setAttribute("aria-modal", "true");
    dialog.setAttribute("aria-labelledby", "instructor-dialog-title");
    const top = element("div", "dialog-top");
    const title = element("h2", "", "선생님 소개");
    title.id = "instructor-dialog-title";
    const close = element("button", "button button-icon", "×");
    close.type = "button";
    close.setAttribute("aria-label", "선생님 소개 닫기");
    top.append(title, close);
    const name = element("h3", "instructor-name", instructor.name || "선생님");
    const affiliation = element("p", "instructor-affiliation", instructor.affiliation || "");
    const email = element("a", "instructor-email");
    emailLink(email, instructor.email);
    const credentials = element("ul", "credentials");
    (Array.isArray(instructor.credentials) ? instructor.credentials : []).forEach(function (credential) {
      credentials.append(element("li", "", credential));
    });
    dialog.append(top, makeAvatar(instructor, true), name, affiliation, email, credentials);
    document.body.append(dialog);

    let opener = null;
    let previousOverflow = "";
    document.querySelectorAll("[data-open-instructor]").forEach(function (button) {
      button.setAttribute("aria-haspopup", "dialog");
      button.setAttribute("aria-controls", dialog.id);
      button.addEventListener("click", function () {
        if (dialog.open) return;
        opener = button;
        previousOverflow = document.body.style.overflow;
        dialog.showModal(); // 네이티브 modal이 배경을 inert로 처리합니다.
        document.body.style.overflow = "hidden";
        close.focus();
      });
    });
    close.addEventListener("click", function () { dialog.close(); });
    dialog.addEventListener("cancel", function (event) { event.preventDefault(); dialog.close(); });
    dialog.addEventListener("close", function () {
      document.body.style.overflow = previousOverflow;
      if (opener && opener.isConnected) opener.focus({ preventScroll: true });
    });
    function outside(event) {
      const rect = dialog.getBoundingClientRect();
      return event.clientX < rect.left || event.clientX > rect.right
        || event.clientY < rect.top || event.clientY > rect.bottom;
    }
    let backdropStart = false;
    dialog.addEventListener("pointerdown", function (event) { backdropStart = event.target === dialog && outside(event); });
    dialog.addEventListener("click", function (event) {
      if (backdropStart && event.target === dialog && outside(event)) dialog.close();
      backdropStart = false;
    });
    dialog.addEventListener("keydown", function (event) {
      if (event.key !== "Tab") return;
      const focusable = Array.from(dialog.querySelectorAll('button, a[href], input, select, textarea, [tabindex]:not([tabindex="-1"])'))
        .filter(function (node) { return !node.disabled && node.getClientRects().length > 0; });
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    });
  }

  function renderOtherLectures() {
    const container = document.querySelector("[data-other-lectures]");
    if (!container) return;
    container.replaceChildren();
    (Array.isArray(site.otherLectures) ? site.otherLectures : []).forEach(function (lecture) {
      let url;
      try { url = new URL(lecture.url); } catch (_) { return; }
      if (!["https:", "http:"].includes(url.protocol)) return;
      const link = element("a", "lecture-link");
      link.href = url.href;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.append(element("span", "", [lecture.emoji, lecture.title].filter(Boolean).join(" ")));
      const arrow = element("span", "", "↗");
      arrow.setAttribute("aria-hidden", "true");
      link.append(arrow, element("span", "sr-only", " (새 탭에서 열기)"));
      container.append(link);
    });
    const region = document.querySelector("[data-other-lectures-region]");
    if (region) region.hidden = container.children.length === 0;
  }

  function initNav() {
    const nav = document.querySelector("[data-section-nav]");
    const header = document.querySelector("[data-header]");
    if (!nav || !header) return;
    const sections = Array.from(document.querySelectorAll("main .lecture-section[id]"));
    nav.replaceChildren();
    sections.forEach(function (section, index) {
      const heading = section.querySelector("h2");
      const link = element("a", "", heading ? heading.textContent.trim() : "섹션 " + (index + 1));
      link.href = "#" + section.id;
      link.dataset.sectionId = section.id;
      nav.append(link);
    });
    const links = Array.from(nav.querySelectorAll('a[href^="#"]'));
    const menu = element("div", "section-menu");
    const controls = element("div", "section-menu-controls");
    const toggle = element("button", "button section-menu-toggle");
    const icon = element("span", "hamburger-icon");
    const progress = element("span", "section-progress", "0 / " + sections.length);
    toggle.type = "button";
    toggle.id = "section-menu-toggle";
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-controls", "section-menu-list");
    toggle.setAttribute("aria-label", "섹션 목록 열기");
    icon.setAttribute("aria-hidden", "true");
    icon.append(element("span"), element("span"), element("span"));
    toggle.append(icon, element("span", "section-menu-label", "목차"));
    progress.dataset.sectionProgress = "";
    progress.setAttribute("aria-live", "polite");
    progress.setAttribute("aria-label", "열람한 섹션 0개, 전체 " + sections.length + "개");
    controls.append(toggle, progress);
    nav.id = "section-menu-list";
    nav.hidden = true;
    nav.setAttribute("aria-labelledby", toggle.id);
    nav.before(menu);
    menu.append(controls, nav);

    function isOpen() {
      return toggle.getAttribute("aria-expanded") === "true";
    }
    function openMenu(focusIndex) {
      if (!links.length) return;
      nav.hidden = false;
      menu.classList.add("is-open");
      toggle.setAttribute("aria-expanded", "true");
      toggle.setAttribute("aria-label", "섹션 목록 닫기");
      if (typeof focusIndex === "number") links[focusIndex].focus();
    }
    function closeMenu(restoreFocus) {
      if (!isOpen()) return;
      nav.hidden = true;
      menu.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-label", "섹션 목록 열기");
      if (restoreFocus) toggle.focus({ preventScroll: true });
    }
    toggle.addEventListener("click", function () {
      if (isOpen()) closeMenu(true);
      else openMenu();
    });
    toggle.addEventListener("keydown", function (event) {
      if (event.key === "ArrowDown" || event.key === "ArrowUp") {
        event.preventDefault();
        openMenu(event.key === "ArrowDown" ? 0 : links.length - 1);
      }
    });
    nav.addEventListener("keydown", function (event) {
      if (!isOpen()) return;
      const current = links.indexOf(document.activeElement);
      let next = current;
      if (event.key === "ArrowDown") next = current < 0 ? 0 : (current + 1) % links.length;
      else if (event.key === "ArrowUp") next = current < 0 ? links.length - 1 : (current - 1 + links.length) % links.length;
      else if (event.key === "Home") next = 0;
      else if (event.key === "End") next = links.length - 1;
      else if (event.key === "Escape") {
        event.preventDefault();
        closeMenu(true);
        return;
      } else return;
      event.preventDefault();
      links[next].focus();
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && isOpen()) {
        event.preventDefault();
        closeMenu(true);
      }
    });
    document.addEventListener("pointerdown", function (event) {
      if (isOpen() && !menu.contains(event.target)) {
        closeMenu(true);
        // Native pointer focus runs after pointerdown. Restore blank-area clicks
        // without stealing focus from another button, link, or input.
        requestAnimationFrame(function () {
          if (document.activeElement === document.body || document.activeElement === document.getElementById("main") || nav.contains(document.activeElement)) {
            toggle.focus({ preventScroll: true });
          }
        });
      }
    });
    document.addEventListener("lecture:presentation-enter", function () { closeMenu(true); });

    const hero = document.getElementById("top");
    let activeId = "";
    function activate(id) {
      if (activeId === id) return;
      activeId = id;
      links.forEach(function (link) {
        if (link.hash === "#" + id) {
          link.setAttribute("aria-current", "location");
        } else link.removeAttribute("aria-current");
      });
    }
    links.forEach(function (link) {
      link.addEventListener("click", function () {
        activate(link.hash.slice(1));
        closeMenu(false);
        requestAnimationFrame(function () {
          if (nav.hidden) toggle.focus({ preventScroll: true });
        });
      });
    });
    let observer;
    let headerHeight = 0;
    function measure() {
      const height = Math.ceil(header.getBoundingClientRect().height);
      if (height === headerHeight) return;
      headerHeight = height;
      root.style.setProperty("--header-offset", height + 16 + "px");
      if (!("IntersectionObserver" in window)) return;
      if (observer) observer.disconnect();
      const visible = new Set();
      observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) visible.add(entry.target);
          else visible.delete(entry.target);
        });
        // 앵커 위 여백 때문에 이전 섹션의 끝이 남아 있어도 새 섹션을 활성화합니다.
        const current = sections.filter(function (section) { return visible.has(section); }).pop();
        if (current) activate(current.id);
        else if (hero && visible.has(hero)) activate("");
      }, { rootMargin: "-" + height + "px 0px -55% 0px", threshold: 0 });
      sections.forEach(function (section) { observer.observe(section); });
      if (hero) observer.observe(hero);
    }
    measure();
    if ("ResizeObserver" in window) new ResizeObserver(measure).observe(header);
    else window.addEventListener("resize", measure, { passive: true });
  }

  function initSectionProgress() {
    const sections = Array.from(document.querySelectorAll("main .lecture-section[id]"));
    const slug = String(currentLevel().slug || "lecture");
    const key = "lecture-progress:" + String((site.site || {}).repo || "lecture") + ":" + slug;
    let visited = [];
    try {
      const saved = JSON.parse(localStorage.getItem(key) || "[]");
      if (Array.isArray(saved)) visited = saved.filter(function (id) { return sections.some(function (section) { return section.id === id; }); });
    } catch (_) { visited = []; }

    function render() {
      document.querySelectorAll("[data-section-nav] a[data-section-id]").forEach(function (link) {
        const done = visited.includes(link.dataset.sectionId);
        const old = link.querySelector(".section-check");
        if (done && !old) {
          const check = element("span", "section-check", "✓");
          check.setAttribute("aria-label", "열람 완료");
          link.prepend(check);
        } else if (!done && old) old.remove();
      });
      const progress = document.querySelector("[data-section-progress]");
      if (progress) {
        progress.textContent = visited.length + " / " + sections.length;
        progress.setAttribute("aria-label", "열람한 섹션 " + visited.length + "개, 전체 " + sections.length + "개");
      }
    }

    function mark(section) {
      if (!section || visited.includes(section.id)) return;
      visited.push(section.id);
      try { localStorage.setItem(key, JSON.stringify(visited)); } catch (_) { /* 저장 불가 환경에서도 현재 화면 표시는 유지합니다. */ }
      render();
    }
    sections.forEach(function (section) {
      section.addEventListener("lecture:section-viewed", function () { mark(section); });
    });
    render();
    if (!("IntersectionObserver" in window)) return;
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { mark(entry.target); observer.unobserve(entry.target); }
      });
    }, { rootMargin: "0px 0px -45% 0px", threshold: 0 });
    sections.forEach(function (section) { if (!visited.includes(section.id)) observer.observe(section); });
  }

  function initPresentationMode() {
    const sections = Array.from(document.querySelectorAll("main .lecture-section[id]"));
    const button = document.querySelector("[data-presentation-toggle]");
    if (!sections.length || !button) return;

    // Equal nonempty data-slide values group existing elements without changing
    // reading layout. Empty values each start a slide. A template can reference
    // an existing pre by ID: data-slide-code + data-slide-lines (no duplicate code).
    const allSlides = [];
    sections.forEach(function (section, sectionIndex) {
      const groups = new Map();
      const markers = Array.from(section.querySelectorAll("[data-slide]"));
      if (!markers.length) markers.push(section);
      markers.forEach(function (marker) {
        const key = marker.dataset.slide || Symbol();
        let slide = groups.get(key);
        if (!slide) {
          slide = { section, sectionIndex, title: marker.dataset.slideTitle || "", markers: [] };
          groups.set(key, slide);
          allSlides.push(slide);
        }
        slide.markers.push(marker);
        if (marker.hasAttribute("data-slide-skip")) slide.skip = true;
      });
    });
    let includeSkipped = false;
    let slides = allSlides.filter(function (slide) { return !slide.skip; });
    const stage = element("div", "presentation-stage");
    stage.hidden = true;
    stage.tabIndex = -1;
    stage.setAttribute("role", "region");
    stage.setAttribute("aria-label", "발표 화면");
    const title = element("h2", "presentation-title");
    const viewport = element("div", "presentation-viewport");
    viewport.tabIndex = 0;
    viewport.setAttribute("aria-label", "발표 조각 내용");
    const content = element("div", "presentation-content");
    const fitFrame = element("div", "presentation-fit-frame");
    const overflowHint = element("p", "presentation-overflow-hint", "↓ 내용이 더 있습니다. 이 영역에서 스크롤하세요.");
    overflowHint.hidden = true;
    fitFrame.append(content);
    viewport.append(fitFrame);
    stage.append(title, viewport, overflowHint);
    const hud = element("div", "presentation-hud");
    hud.hidden = true;
    hud.setAttribute("role", "status");
    hud.setAttribute("aria-live", "polite");
    const counter = element("strong", "presentation-counter");
    const skipStatus = element("span", "presentation-skip-status");
    hud.append(counter, skipStatus, element("span", "", "← → 조각 · Shift + 방향키 섹션 · B 블랙아웃 · P / Esc 종료"));
    const blackout = element("div", "presentation-blackout");
    blackout.hidden = true;
    blackout.setAttribute("aria-hidden", "true");
    document.body.append(stage, hud, blackout);
    let index = 0;
    let returnFocus = null;
    let moved = [];
    let annotations = [];
    let fitting = false;
    let auditing = false;
    let transition = null;
    const imageStyles = new Map();
    const overflow = new Map();
    const warned = new Set();
    const presenting = function () { return !stage.hidden; };
    function dialogOpen() {
      return Array.from(document.querySelectorAll("dialog")).some(function (dialog) { return dialog.open; });
    }
    function restore() {
      imageStyles.forEach(function (style, img) {
        if (style === null) img.removeAttribute("style");
        else img.setAttribute("style", style);
      });
      imageStyles.clear();
      if (transition) { transition.cancel(); transition = null; }
      annotations.forEach(function (note) { note.remove(); });
      annotations = [];
      content.querySelectorAll(".is-slide-line-hidden").forEach(function (line) {
        line.classList.remove("is-slide-line-hidden");
      });
      moved.reverse().forEach(function (entry) {
        entry.placeholder.replaceWith(entry.node);
      });
      moved = [];
    }
    function move(node) {
      if (content.contains(node)) return;
      const placeholder = document.createComment("presentation: original position");
      node.before(placeholder);
      moved.push({ node, placeholder });
      content.append(node);
    }
    function sliceCode(pre, range) {
      const match = /^(\d+)-(\d+)$/.exec(range || "");
      if (!match) return;
      const lines = Array.from(pre.querySelectorAll(".code-line"));
      // A trailing LF creates an empty display span, not another source line.
      const total = lines.length - (lines.length > 1 && !lines[lines.length - 1].querySelector(".line-content").textContent ? 1 : 0);
      const first = Math.max(1, Math.min(total, Number(match[1])));
      const last = Math.max(first, Math.min(total, Number(match[2])));
      lines.forEach(function (line, i) { line.classList.toggle("is-slide-line-hidden", i + 1 < first || i + 1 > last); });
      const note = element("span", "presentation-code-range", first + "번 줄 ~ " + last + "번 줄 / 전체 " + total + "줄");
      pre.closest(".code-block").querySelector(".code-toolbar").append(note);
      annotations.push(note);
    }
    function fit() {
      if (!presenting() || fitting) return;
      fitting = true;
      overflowHint.hidden = true;
      viewport.classList.remove("has-overflow");
      fitFrame.classList.remove("is-scaled");
      fitFrame.style.height = "";
      content.style.transform = "";
      const slide = slides[index];
      const widget = content.querySelector("[data-widget]");
      const images = Array.from(content.querySelectorAll("figure img"));
      const contain = !!widget || images.length > 0 || (slide && slide.markers.some(function (marker) { return marker.dataset.slideFit === "contain"; }));
      stage.dataset.fitType = contain ? "contain" : "text";
      stage.dataset.fitScale = "1";
      const sizes = contain ? [[28, 24]] : [[28, 24], [27, 23], [26, 22], [25, 21], [24, 20]];
      for (const size of sizes) {
        stage.style.setProperty("--slide-body", size[0] + "px");
        stage.style.setProperty("--slide-code", size[1] + "px");
        if (viewport.scrollHeight <= viewport.clientHeight && content.scrollHeight <= viewport.clientHeight - 2) break;
      }
      if (contain && images.length && !widget) {
        images.forEach(function (img) {
          if (!imageStyles.has(img)) imageStyles.set(img, img.getAttribute("style"));
          img.style.height = "auto";
          img.style.maxHeight = "none";
        });
        const imageHeight = images.reduce(function (sum, img) { return sum + img.getBoundingClientRect().height; }, 0);
        const otherHeight = content.scrollHeight - imageHeight;
        const available = Math.max(1, (viewport.clientHeight - otherHeight - 2) / images.length);
        images.forEach(function (img) { img.style.maxHeight = available + "px"; });
      } else if (contain) {
        // A transform alone leaves the unscaled layout box in the scroll area.
        // The frame takes the rendered height; top origin prevents upper clipping.
        const naturalHeight = content.scrollHeight;
        const scale = Math.max(0.6, Math.min(1, (viewport.clientHeight - 2) / Math.max(1, naturalHeight), viewport.clientWidth / Math.max(1, content.scrollWidth)));
        if (scale < 1) {
          fitFrame.classList.add("is-scaled");
          fitFrame.style.height = Math.ceil(naturalHeight * scale) + "px";
          content.style.transform = "scale(" + scale + ")";
        }
        stage.dataset.fitScale = scale.toFixed(4);
      }
      // Measure the actual scroll container, not the document or only its child.
      const excess = viewport.scrollHeight - viewport.clientHeight;
      if (excess > 0) {
        const item = { slide: index + 1, section: slide ? slide.section.id : "", title: title.textContent, scrollHeight: viewport.scrollHeight, clientHeight: viewport.clientHeight, overflowPx: excess, type: stage.dataset.fitType, scale: stage.dataset.fitScale };
        overflow.set(index, item);
        overflowHint.hidden = false;
        viewport.classList.add("has-overflow");
        if (!auditing && !warned.has(index)) {
          console.warn("[발표 조각 넘침] 더 작은 조각으로 나누세요.", item);
          warned.add(index);
        }
      } else overflow.delete(index);
      fitting = false;
    }
    function show(nextIndex, silent) {
      restore();
      skipStatus.textContent = "S · 건너뛴 조각 " + (includeSkipped ? "포함" : "제외");
      stage.dataset.includeSkipped = String(includeSkipped);
      if (!slides.length) {
        index = 0;
        stage.dataset.slideIndex = "0";
        stage.dataset.section = "";
        title.textContent = "표시할 조각이 없습니다. S를 눌러 전체 조각을 확인하세요.";
        counter.textContent = "0 / 0 · 섹션 0/" + sections.length;
        overflowHint.hidden = true;
        stage.focus({ preventScroll: true });
        return;
      }
      index = Math.max(0, Math.min(slides.length - 1, nextIndex));
      const slide = slides[index];
      const sectionTitle = slide.section.querySelector("h2").textContent.trim();
      title.textContent = sectionTitle + (slide.title && slide.title !== sectionTitle ? " · " + slide.title : "");
      slide.markers.forEach(function (marker) {
        // Optional teaching outline; S restores the unchanged original range.
        const preview = !includeSkipped && marker.dataset.slidePreview;
        const source = preview ? document.getElementById(preview) : marker.dataset.slideCode ? document.getElementById(marker.dataset.slideCode) : marker;
        if (!source) return;
        const node = source.matches("pre[data-code]") ? source.closest(".code-block") : source;
        move(node);
        if (source.matches("pre[data-code]")) sliceCode(source, preview ? source.dataset.slideLines : marker.dataset.slideLines);
        else source.querySelectorAll("pre[data-slide-lines]").forEach(function (pre) { sliceCode(pre, pre.dataset.slideLines); });
      });
      content.querySelectorAll("pre[data-code]").forEach(function (pre) {
        const last = pre.querySelector(".code-line:last-child");
        if (last && !last.querySelector(".line-content").textContent) last.classList.add("is-slide-line-hidden");
      });
      stage.dataset.slideIndex = String(index + 1);
      stage.dataset.section = slide.section.id;
      counter.textContent = (index + 1) + " / " + slides.length + " · 섹션 " + (slide.sectionIndex + 1) + "/" + sections.length;
      viewport.scrollTop = 0;
      fit();
      if (!silent) {
        slide.section.dispatchEvent(new CustomEvent("lecture:section-viewed"));
        stage.focus({ preventScroll: true });
        if (!reducedMotion.matches) transition = content.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 120 });
      }
    }
    function enter() {
      if (dialogOpen()) return;
      includeSkipped = false;
      slides = allSlides.filter(function (slide) { return !slide.skip; });
      overflow.clear();
      warned.clear();
      document.dispatchEvent(new CustomEvent("lecture:presentation-enter"));
      returnFocus = document.activeElement;
      const current = document.querySelector('[data-section-nav] a[aria-current="location"]');
      const start = current ? slides.findIndex(function (slide) { return slide.section.id === current.dataset.sectionId; }) : 0;
      // Do not reveal answers on entry. Later visits preserve the teacher's choice.
      sections.forEach(function (section) { section.querySelectorAll("details").forEach(function (detail) { detail.open = false; }); });
      document.body.classList.add("is-presenting");
      button.setAttribute("aria-pressed", "true");
      stage.hidden = hud.hidden = blackout.hidden = false;
      show(start >= 0 ? start : 0);
    }
    function exit() {
      const section = slides[index] ? slides[index].section : sections[0];
      restore();
      stage.hidden = hud.hidden = blackout.hidden = true;
      document.body.classList.remove("is-presenting", "is-blackout");
      blackout.setAttribute("aria-hidden", "true");
      button.setAttribute("aria-pressed", "false");
      section.scrollIntoView({ block: "start", behavior: reducedMotion.matches ? "auto" : "smooth" });
      if (returnFocus && returnFocus.isConnected) returnFocus.focus({ preventScroll: true });
    }
    // Scan every slide at the current viewport; no section progress is recorded.
    // Call in DevTools while presenting: reportPresentationOverflow().
    window.reportPresentationOverflow = function () {
      if (!presenting()) { console.info("P로 발표 모드에 들어간 뒤 다시 실행하세요."); return []; }
      const saved = index;
      const focused = document.activeElement;
      const scroll = viewport.scrollTop;
      auditing = true;
      overflow.clear();
      slides.forEach(function (_, i) { show(i, true); });
      const result = Array.from(overflow.values());
      show(saved, true);
      auditing = false;
      viewport.scrollTop = scroll;
      if (focused && focused.isConnected) focused.focus({ preventScroll: true });
      console.table(result);
      console.info("발표 조각 " + slides.length + "개 검사 · 넘침 " + result.length + "개");
      return result;
    };
    button.setAttribute("aria-pressed", "false");
    button.addEventListener("click", function () { if (presenting()) exit(); else enter(); });
    window.addEventListener("resize", fit);
    // Images, widget content and opening a details answer can change the height.
    if ("ResizeObserver" in window) new ResizeObserver(function () { fit(); }).observe(content);
    content.addEventListener("load", fit, true);
    content.addEventListener("toggle", fit, true);
    document.addEventListener("keydown", function (event) {
      if (event.defaultPrevented || event.repeat || event.altKey || event.ctrlKey || event.metaKey || dialogOpen()) return;
      const target = event.target;
      if (target instanceof Element && (target.matches("input, textarea, select") || target.isContentEditable)) return;
      if (event.key.toLowerCase() === "p") { event.preventDefault(); if (presenting()) exit(); else enter(); return; }
      if (!presenting()) return;
      const backwards = ["ArrowLeft", "ArrowUp", "PageUp"].includes(event.key);
      const forwards = ["ArrowRight", "ArrowDown", "PageDown"].includes(event.key);
      if ((backwards || forwards) && target instanceof Element && target.closest("[data-widget]")) return;
      if (event.key === "Escape") { event.preventDefault(); exit(); }
      else if (event.key.toLowerCase() === "s") {
        event.preventDefault();
        const current = slides[index];
        const originalIndex = allSlides.indexOf(current);
        includeSkipped = !includeSkipped;
        slides = allSlides.filter(function (slide) { return includeSkipped || !slide.skip; });
        let next = slides.indexOf(current);
        if (next < 0) next = slides.findIndex(function (slide) { return allSlides.indexOf(slide) > originalIndex; });
        overflow.clear();
        warned.clear();
        show(next >= 0 ? next : slides.length - 1);
      } else if (backwards || forwards) {
        event.preventDefault();
        if (!slides.length) return;
        const direction = backwards ? -1 : 1;
        if (event.shiftKey && event.key.startsWith("Arrow")) {
          const visibleSections = Array.from(new Set(slides.map(function (slide) { return slide.sectionIndex; })));
          const currentSection = visibleSections.indexOf(slides[index].sectionIndex);
          const targetSection = visibleSections[Math.max(0, Math.min(visibleSections.length - 1, currentSection + direction))];
          show(slides.findIndex(function (slide) { return slide.sectionIndex === targetSection; }));
        } else show(index + direction);
      } else if (event.key.toLowerCase() === "b") {
        event.preventDefault();
        const active = document.body.classList.toggle("is-blackout");
        blackout.setAttribute("aria-hidden", String(!active));
      }
    });
  }

  function initProgressBar() {
    const bar = document.querySelector("[data-progress]");
    if (!bar) return;
    let scheduled = false;
    function update() {
      scheduled = false;
      const available = root.scrollHeight - root.clientHeight;
      const value = available > 0 ? Math.max(0, Math.min(1, window.scrollY / available)) : 0;
      bar.style.transform = "scaleX(" + value + ")";
    }
    function schedule() {
      if (scheduled) return;
      scheduled = true;
      requestAnimationFrame(update);
    }
    window.addEventListener("scroll", schedule, { passive: true });
    window.addEventListener("resize", schedule, { passive: true });
    if ("ResizeObserver" in window) new ResizeObserver(schedule).observe(document.body);
    update();
  }

  function pythonTokens(source) {
    // 최소 토큰 분석: 주석·일반/삼중 따옴표 문자열·예약어·숫자·기본 내장 함수.
    // AST 분석이나 f-string 내부의 세부 강조는 하지 않습니다. HTML 대신 textContent로 처리합니다.
    const pattern = /#[^\n]*|(?:[rubf]{0,2})(?:"""[\s\S]*?(?:"""|$)|'''[\s\S]*?(?:'''|$)|"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*')|\b(?:False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield|match|case)\b|\b(?:0[xX][\da-fA-F_]+|\d[\d_]*(?:\.\d[\d_]*)?(?:[eE][+-]?\d+)?)\b|\b(?:print|range|len|sum|input|int|float|str|list|dict|set|tuple|enumerate|zip)\b/g;
    const tokens = [];
    let offset = 0;
    for (const match of source.matchAll(pattern)) {
      if (match.index > offset) tokens.push({ text: source.slice(offset, match.index), kind: "" });
      const value = match[0];
      let kind = "keyword";
      if (value.startsWith("#")) kind = "comment";
      else if (/^[rubf]*["']/i.test(value)) kind = "string";
      else if (/^\d/.test(value)) kind = "number";
      else if (/^(print|range|len|sum|input|int|float|str|list|dict|set|tuple|enumerate|zip)$/.test(value)) kind = "function";
      tokens.push({ text: value, kind: kind });
      offset = match.index + value.length;
    }
    if (offset < source.length) tokens.push({ text: source.slice(offset), kind: "" });
    return tokens;
  }

  function highlightedLines(spec, total) {
    const lines = new Set();
    String(spec || "").split(",").forEach(function (part) {
      const match = part.trim().match(/^(\d+)(?:\s*-\s*(\d+))?$/);
      if (!match) return;
      const start = Math.max(1, Number(match[1]));
      const end = Math.min(total, Number(match[2] || match[1]));
      for (let n = start; n <= end; n += 1) lines.add(n);
    });
    return lines;
  }

  async function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      try { await navigator.clipboard.writeText(text); return true; } catch (_) { /* file:// 등에서는 아래 대체 경로 */ }
    }
    const previousFocus = document.activeElement;
    const selection = window.getSelection();
    const ranges = [];
    if (selection) for (let i = 0; i < selection.rangeCount; i += 1) ranges.push(selection.getRangeAt(i).cloneRange());
    const field = element("textarea", "sr-only");
    field.value = text;
    field.setAttribute("aria-label", "복사할 코드");
    document.body.append(field);
    field.focus({ preventScroll: true });
    field.select();
    let copied = false;
    try { copied = document.execCommand("copy"); } catch (_) { copied = false; }
    field.remove();
    if (selection) { selection.removeAllRanges(); ranges.forEach(function (range) { selection.addRange(range); }); }
    if (previousFocus) previousFocus.focus({ preventScroll: true });
    return copied;
  }

  function initCodeBlocks() {
    document.querySelectorAll("pre[data-code]:not([data-code-ready])").forEach(function (pre, index) {
      const source = (pre.querySelector("code") || pre).textContent.replace(/\r\n?/g, "\n");
      const language = pre.dataset.language || "python";
      const label = pre.dataset.label || language;
      const code = element("code");
      const lineContents = [];
      const selected = highlightedLines(pre.dataset.highlight, source.split("\n").length);
      source.split("\n").forEach(function (_, i) {
        const line = element("span", "code-line" + (selected.has(i + 1) ? " is-highlighted" : ""));
        line.dataset.line = String(i + 1);
        const number = element("span", "line-number", i + 1);
        number.setAttribute("aria-hidden", "true");
        const content = element("span", "line-content");
        line.append(number, content);
        code.append(line);
        lineContents.push(content);
      });
      let currentLine = 0;
      const tokens = language.toLowerCase() === "python" ? pythonTokens(source) : [{ text: source, kind: "" }];
      tokens.forEach(function (token) {
        token.text.split("\n").forEach(function (part, i) {
          if (i > 0) currentLine += 1;
          if (part) lineContents[currentLine].append(token.kind ? element("span", "syntax-" + token.kind, part) : document.createTextNode(part));
        });
      });
      const wrapper = element("div", "code-block");
      const toolbar = element("div", "code-toolbar");
      const caption = element("span", "code-label", label);
      const button = element("button", "copy-button", "복사");
      button.type = "button";
      button.setAttribute("aria-label", "코드 " + (index + 1) + " 복사");
      let resetTimer;
      button.addEventListener("click", async function () {
        const success = await copyText(source);
        const message = success ? "복사 완료" : "복사 실패";
        button.textContent = message;
        const status = document.querySelector("[data-copy-status]");
        if (status) status.textContent = success ? "코드 " + (index + 1) + "을 클립보드에 복사했습니다."
          : "자동 복사가 차단되었습니다. 코드 영역을 선택해 직접 복사해 주세요.";
        clearTimeout(resetTimer);
        resetTimer = setTimeout(function () { button.textContent = "복사"; if (status) status.textContent = ""; }, 2200);
      });
      toolbar.append(caption, button);
      pre.before(wrapper);
      wrapper.append(toolbar, pre);
      pre.replaceChildren(code);
      pre.dataset.codeReady = "true";
      pre.tabIndex = 0;
      pre.setAttribute("aria-label", label + (selected.size ? ", 강조 줄 " + Array.from(selected).join(", ") : ""));
    });
  }

  function initReveal() {
    const sections = Array.from(document.querySelectorAll("[data-reveal]"));
    if (reducedMotion.matches || !("IntersectionObserver" in window)) return;
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.remove("is-reveal-pending");
        observer.unobserve(entry.target);
      });
    }, { threshold: 0, rootMargin: "0px 0px -24px 0px" });
    sections.forEach(function (section) {
      // 보이는 첫 화면과 해시로 이동한 섹션은 숨기지 않습니다.
      if (section.getBoundingClientRect().top < window.innerHeight) return;
      section.classList.add("reveal-enabled", "is-reveal-pending");
      observer.observe(section);
    });
    function stop() {
      if (!reducedMotion.matches) return;
      observer.disconnect();
      sections.forEach(function (section) { section.classList.remove("is-reveal-pending", "reveal-enabled"); });
    }
    reducedMotion.addEventListener("change", stop);
    // 키보드로 진입한 콘텐츠는 애니메이션을 기다리지 않고 표시합니다.
    sections.forEach(function (section) {
      section.addEventListener("focusin", function () { section.classList.remove("is-reveal-pending"); observer.unobserve(section); });
    });
  }

  function initThemeToggle() {
    const button = document.querySelector("[data-theme-toggle]");
    if (!button) return;
    function update() {
      const dark = root.dataset.theme === "dark";
      button.setAttribute("aria-label", dark ? "라이트 모드로 전환" : "다크 모드로 전환");
      button.setAttribute("aria-pressed", String(dark));
      button.title = dark ? "라이트 모드로 전환" : "다크 모드로 전환";
      const path = button.querySelector("path");
      if (path) path.setAttribute("d", dark
        ? "M12 3V1m0 22v-2M3 12H1m22 0h-2M5.6 5.6 4.2 4.2m15.6 15.6-1.4-1.4M5.6 18.4l-1.4 1.4M19.8 4.2l-1.4 1.4M17 12a5 5 0 1 1-10 0 5 5 0 0 1 10 0"
        : "M20.9 13a9 9 0 0 1-9.9-9.9A9 9 0 1 0 20.9 13Z");
    }
    button.addEventListener("click", function () {
      preferredTheme = root.dataset.theme === "dark" ? "light" : "dark";
      root.dataset.theme = preferredTheme;
      try { localStorage.setItem(themeKey, preferredTheme); } catch (_) { /* 현재 탭의 테마는 유지합니다. */ }
      update();
    });
    systemTheme.addEventListener("change", function (event) {
      if (preferredTheme) return;
      root.dataset.theme = event.matches ? "dark" : "light";
      update();
    });
    update();
  }

  function init() {
    preparePage();
    applyLectureMeta();
    renderInstructorModal();
    renderOtherLectures();
    initThemeToggle();
    if (currentLevel()) {
      initCodeBlocks();
      initNav();
      initSectionProgress();
      initPresentationMode();
      initProgressBar();
      initReveal();
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();
