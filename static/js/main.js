// Mobile nav toggle
(function () {
  const nav = document.getElementById("site-nav");
  const toggle = document.getElementById("nav-toggle");
  if (!nav || !toggle) return;

  toggle.addEventListener("click", function () {
    const isOpen = nav.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
  });
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
