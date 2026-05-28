/* Nimbus Academy PWA — client app */

(function () {
  "use strict";

  const docs = window.NIMBUS_CONTENT || [];
  const $ = (sel) => document.querySelector(sel);

  const els = {
    docList: $("#doc-list"),
    content: $("#content"),
    pageTitle: $("#page-title"),
    pageSubtitle: $("#page-subtitle"),
    onlineStatus: $("#online-status"),
    installBtn: $("#install-btn"),
    sidebar: $("#sidebar"),
    overlay: $("#overlay"),
    themeToggle: $("#theme-toggle"),
  };

  let deferredPrompt = null;
  let activeId = null;

  marked.setOptions({
    gfm: true,
    breaks: false,
    headerIds: true,
    mangle: false,
  });

  function setOnlineStatus() {
    const online = navigator.onLine;
    els.onlineStatus.textContent = online ? "Online" : "Offline";
    els.onlineStatus.className = "status-pill " + (online ? "online" : "offline");
  }

  function renderMath(root) {
    if (typeof renderMathInElement !== "function") return;
    renderMathInElement(root, {
      delimiters: [
        { left: "$$", right: "$$", display: true },
        { left: "$", right: "$", display: false },
      ],
      throwOnError: false,
    });
  }

  function bindInArticleLinks(root) {
    root.querySelectorAll('a[href^="#"]').forEach((link) => {
      link.addEventListener("click", (e) => {
        const hash = link.getAttribute("href").slice(1);
        if (!hash) return;
        const target = root.querySelector(`#${CSS.escape(hash)}`);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: "smooth", block: "start" });
          history.replaceState({ docId: activeId }, "", `#${activeId}`);
        }
      });
    });
  }

  function renderMarkdown(md) {
    return marked.parse(md);
  }

  function openDoc(id, pushState = true) {
    const doc = docs.find((d) => d.id === id);
    if (!doc) return;

    activeId = id;
    els.pageTitle.textContent = doc.title;
    els.pageSubtitle.textContent = doc.subtitle;

    document.querySelectorAll(".doc-btn").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.id === id);
    });

    const article = document.createElement("article");
    article.className = "doc-article";
    article.innerHTML = renderMarkdown(doc.markdown);
    bindInArticleLinks(article);

    els.content.innerHTML = "";
    els.content.appendChild(article);
    renderMath(article);

    if (pushState) {
      history.pushState({ docId: id }, "", `#${id}`);
    }

    closeSidebar();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function buildSidebar() {
    els.docList.innerHTML = "";
    docs.forEach((doc) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "doc-btn";
      btn.dataset.id = doc.id;
      btn.innerHTML =
        `<span class="doc-icon">${doc.icon}</span>` +
        `<span class="doc-title">${doc.title}</span>` +
        `<span class="doc-sub">${doc.subtitle}</span>`;
      btn.addEventListener("click", () => openDoc(doc.id));
      els.docList.appendChild(btn);
    });
  }

  function openSidebar() {
    els.sidebar.classList.add("open");
    els.overlay.hidden = false;
  }

  function closeSidebar() {
    els.sidebar.classList.remove("open");
    els.overlay.hidden = true;
  }

  function loadTheme() {
    const saved = localStorage.getItem("nimbus-theme");
    if (saved === "dark") document.documentElement.setAttribute("data-theme", "dark");
  }

  function toggleTheme() {
    const dark = document.documentElement.getAttribute("data-theme") === "dark";
    if (dark) {
      document.documentElement.removeAttribute("data-theme");
      localStorage.setItem("nimbus-theme", "light");
    } else {
      document.documentElement.setAttribute("data-theme", "dark");
      localStorage.setItem("nimbus-theme", "dark");
    }
  }

  function registerServiceWorker() {
    if (!("serviceWorker" in navigator)) return;
    const swUrl = new URL("sw.js", window.location.href);
    if (swUrl.protocol === "file:") return;

    navigator.serviceWorker.register("sw.js").catch((err) => {
      console.warn("SW registration failed:", err);
    });
  }

  function routeFromHash() {
    const hash = location.hash.replace("#", "");
    if (hash && docs.some((d) => d.id === hash)) {
      openDoc(hash, false);
    }
  }

  window.addEventListener("online", setOnlineStatus);
  window.addEventListener("offline", setOnlineStatus);
  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    deferredPrompt = e;
    els.installBtn.hidden = false;
  });
  window.addEventListener("appinstalled", () => {
    deferredPrompt = null;
    els.installBtn.hidden = true;
  });
  window.addEventListener("popstate", (e) => {
    if (e.state && e.state.docId) openDoc(e.state.docId, false);
  });

  $("#sidebar-open")?.addEventListener("click", openSidebar);
  $("#sidebar-close")?.addEventListener("click", closeSidebar);
  els.overlay?.addEventListener("click", closeSidebar);
  els.themeToggle?.addEventListener("click", toggleTheme);
  els.installBtn?.addEventListener("click", async () => {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    await deferredPrompt.userChoice;
    deferredPrompt = null;
    els.installBtn.hidden = true;
  });

  loadTheme();
  setOnlineStatus();
  buildSidebar();
  registerServiceWorker();
  routeFromHash();

  if (docs.length === 1) openDoc(docs[0].id, false);
})();
