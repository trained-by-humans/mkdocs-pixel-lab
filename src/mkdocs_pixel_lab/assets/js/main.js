document.addEventListener("DOMContentLoaded", () => {
  const searchShell = document.querySelector(".search-shell");
  const searchToggle = document.querySelector("#search-toggle");
  const searchInput = document.querySelector("#mkdocs-search-query");
  const siteShell = document.querySelector(".site-switcher");
  const siteToggle = document.querySelector("#site-toggle");
  const sitePanel = document.querySelector("#site-panel");
  const navToggle = document.querySelector("#nav-toggle");
  const mobileNav = document.querySelector("#mobile-nav");
  const navClose = document.querySelector("#nav-close");
  const drawerScrim = document.querySelector("#drawer-scrim");
  const skipLink = document.querySelector(".skip-link");

  if (skipLink) {
    document.addEventListener("keydown", (event) => {
      const activeElement = document.activeElement;
      const enteringDocument = activeElement === document.body || activeElement === document.documentElement;
      if (event.key === "Tab" && !event.shiftKey && enteringDocument) {
        event.preventDefault();
        skipLink.focus();
      }
    });
  }

  const setSearchOpen = (open) => {
    if (!searchShell || !searchToggle) return;
    searchShell.classList.toggle("is-open", open);
    searchToggle.setAttribute("aria-expanded", String(open));
    if (open) setSiteOpen(false);
  };

  const setSiteOpen = (open) => {
    if (!siteShell || !siteToggle || !sitePanel) return;
    sitePanel.hidden = !open;
    siteShell.classList.toggle("is-open", open);
    siteToggle.setAttribute("aria-expanded", String(open));
    if (open) setSearchOpen(false);
  };

  const setNavOpen = (open) => {
    if (!navToggle || !mobileNav || !drawerScrim) return;
    mobileNav.classList.toggle("is-open", open);
    drawerScrim.classList.toggle("is-open", open);
    document.body.classList.toggle("drawer-open", open);
    mobileNav.setAttribute("aria-hidden", String(!open));
    navToggle.setAttribute("aria-expanded", String(open));
    if (open) {
      setSiteOpen(false);
      setSearchOpen(false);
    }
  };

  if (searchShell && searchToggle && searchInput) {
    searchToggle.addEventListener("click", () => {
      const open = !searchShell.classList.contains("is-open");
      setSearchOpen(open);
      if (open) window.requestAnimationFrame(() => {
        if (searchShell.classList.contains("is-open")) searchInput.focus();
      });
    });

    document.addEventListener("click", (event) => {
      if (!searchShell.contains(event.target)) setSearchOpen(false);
    });

    searchShell.addEventListener("pointerenter", () => setSiteOpen(false));
    searchShell.addEventListener("focusin", () => setSiteOpen(false));
  }

  if (siteShell && siteToggle && sitePanel) {
    const links = Array.from(sitePanel.querySelectorAll("a"));
    siteToggle.addEventListener("click", () => setSiteOpen(sitePanel.hidden));
    siteToggle.addEventListener("keydown", (event) => {
      if (event.key !== "ArrowDown" && event.key !== "ArrowUp") return;
      event.preventDefault();
      setSiteOpen(true);
      (event.key === "ArrowDown" ? links[0] : links.at(-1))?.focus();
    });
    sitePanel.addEventListener("keydown", (event) => {
      if (!["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) return;
      event.preventDefault();
      const index = links.indexOf(document.activeElement);
      const next = event.key === "Home" ? 0
        : event.key === "End" ? links.length - 1
        : (index + (event.key === "ArrowDown" ? 1 : -1) + links.length) % links.length;
      links[next]?.focus();
    });
    sitePanel.addEventListener("click", (event) => {
      if (event.target.closest("a")) setSiteOpen(false);
    });
    siteShell.addEventListener("focusout", (event) => {
      if (!siteShell.contains(event.relatedTarget)) setSiteOpen(false);
    });
    document.addEventListener("click", (event) => {
      if (!siteShell.contains(event.target)) setSiteOpen(false);
    });
  }

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    if (sitePanel && !sitePanel.hidden) {
      setSiteOpen(false);
      siteToggle.focus();
    } else if (mobileNav?.classList.contains("is-open")) {
      setNavOpen(false);
      navToggle?.focus();
    } else if (searchShell?.contains(document.activeElement) || searchShell?.classList.contains("is-open")) {
      setSearchOpen(false);
      searchToggle?.focus();
    }
  });

  if (navToggle && mobileNav && drawerScrim) {
    navToggle.addEventListener("click", () => {
      const open = !mobileNav.classList.contains("is-open");
      setNavOpen(open);
      if (open) navClose?.focus();
    });
    navClose?.addEventListener("click", () => {
      setNavOpen(false);
      navToggle.focus();
    });
    drawerScrim.addEventListener("click", () => {
      setNavOpen(false);
      navToggle.focus();
    });
  }

  const copyText = async (value) => {
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(value);
        return;
      }
    } catch (error) {
      // Fall back for browsers that block the Clipboard API outside a secure context.
    }

    const textarea = document.createElement("textarea");
    textarea.value = value;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.appendChild(textarea);
    textarea.select();
    const copied = document.execCommand("copy");
    textarea.remove();
    if (!copied) throw new Error("Clipboard copy failed");
  };

  document.querySelectorAll(".main pre > code").forEach((code) => {
    const block = code.closest(".highlight");
    if (!block || block.querySelector(".code-copy")) return;

    const button = document.createElement("button");
    button.className = "code-copy";
    button.type = "button";
    button.textContent = "COPY";
    button.setAttribute("aria-label", "Copy code to clipboard");
    block.appendChild(button);

    button.addEventListener("click", async () => {
      try {
        await copyText(code.innerText);
        button.textContent = "COPIED";
        button.classList.add("is-copied");
      } catch (error) {
        button.textContent = "FAILED";
      }

      window.setTimeout(() => {
        button.textContent = "COPY";
        button.classList.remove("is-copied");
      }, 1600);
    });
  });

  if (document.body.dataset.permalinkIcon === "chain") {
    document.querySelectorAll(".main .headerlink").forEach((anchor) => {
      if (anchor.querySelector(".headerlink__fill")) return;
      const fill = document.createElement("span");
      fill.className = "headerlink__fill";
      fill.setAttribute("aria-hidden", "true");
      anchor.prepend(fill);
    });
  }

  const trackedHeadings = Array.from(
    document.querySelectorAll(".main h2[id], .main h3[id], .main h4[id], .main h5[id], .main h6[id]"),
  );
  let trackingFrame;

  const updateHeadingFragment = () => {
    trackingFrame = undefined;
    const headerHeight = document.querySelector(".header")?.getBoundingClientRect().height ?? 0;
    const tabsHeight = document.querySelector(".tabs")?.getBoundingClientRect().height ?? 0;
    const offset = headerHeight + tabsHeight + 24;
    let activeHeading;

    trackedHeadings.forEach((heading) => {
      if (heading.getBoundingClientRect().top <= offset) activeHeading = heading;
    });

    const hash = activeHeading ? `#${activeHeading.id}` : "";
    if (window.location.hash === hash) return;

    const url = `${window.location.pathname}${window.location.search}${hash}`;
    window.history.replaceState(null, "", url);
  };

  if (trackedHeadings.length) {
    const scheduleHeadingTracking = () => {
      if (trackingFrame !== undefined) return;
      trackingFrame = window.requestAnimationFrame(updateHeadingFragment);
    };

    window.addEventListener("scroll", scheduleHeadingTracking, { passive: true });
    window.addEventListener("resize", scheduleHeadingTracking);
    scheduleHeadingTracking();
  }

  document.querySelectorAll(".main table").forEach((table) => {
    const shell = document.createElement("div");
    shell.className = "table-shell";
    table.parentNode.insertBefore(shell, table);
    const scroll = document.createElement("div");
    scroll.className = "table-scroll";
    shell.appendChild(scroll);
    scroll.appendChild(table);
  });

  document.querySelectorAll(".tabs-demo").forEach((group) => {
    const buttons = group.querySelectorAll("[data-tab]");
    const panels = group.querySelectorAll("[data-panel]");

    buttons.forEach((button) => {
      button.addEventListener("click", () => {
        buttons.forEach((item) => item.classList.toggle("active", item === button));
        panels.forEach((panel) => {
          panel.hidden = panel.dataset.panel !== button.dataset.tab;
        });
      });
    });
  });
});
