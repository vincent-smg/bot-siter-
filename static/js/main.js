// Mobile nav toggle
(function () {
  const nav = document.getElementById("site-nav");
  const toggle = document.getElementById("nav-toggle");
  const panel = document.getElementById("nav-mobile-panel");
  if (!nav || !toggle) return;

  toggle.addEventListener("click", function () {
    const isOpen = nav.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    if (panel) panel.setAttribute("aria-hidden", isOpen ? "false" : "true");
  });

  // Close the panel when a link inside it is clicked
  if (panel) {
    panel.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        panel.setAttribute("aria-hidden", "true");
      });
    });
  }
})();

// Auto-dismiss flash messages
(function () {
  const stack = document.getElementById("flash-stack");
  if (!stack) return;

  setTimeout(function () {
    stack.querySelectorAll(".flash").forEach(function (el) {
      el.style.transition = "opacity 0.4s ease";
      el.style.opacity = "0";
    });
    setTimeout(function () {
      stack.remove();
    }, 450);
  }, 4500);
})();
