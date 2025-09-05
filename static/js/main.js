(function () {
  function openLightbox(src) {
    const lb = document.getElementById("lightbox");
    const img = document.getElementById("lightbox-img");
    if (!lb || !img) return;
    img.src = src;
    lb.style.display = "flex";
    lb.setAttribute("aria-hidden", "false");
    document.body.classList.add("no-scroll");
  }

  function closeLightbox() {
    const lb = document.getElementById("lightbox");
    const img = document.getElementById("lightbox-img");
    if (!lb || !img) return;
    lb.style.display = "none";
    lb.setAttribute("aria-hidden", "true");
    img.removeAttribute("src");
    document.body.classList.remove("no-scroll");
  }

  function zoomTargetFrom(eventTarget) {
    const img = eventTarget.closest(".zoomable");
    if (img) return img;
    const box = eventTarget.closest(".imgbox");
    if (box) return box.querySelector(".zoomable");
    return null;
  }

  function kill(e) {
    e.preventDefault();
    e.stopPropagation();
    if (e.stopImmediatePropagation) e.stopImmediatePropagation();
  }

  ["mousedown", "touchstart", "click"].forEach((type) => {
    document.addEventListener(
      type,
      (e) => {
        const z = zoomTargetFrom(e.target);
        if (!z) return;
        kill(e);
        if (type === "click") {
          const src = z.getAttribute("data-zoom-src") || z.currentSrc || z.src;
          if (src) openLightbox(src);
        }
      },
      true
    );
  });

  document.addEventListener(
    "click",
    (e) => {
      if (e.target.id === "lightbox" || e.target.id === "lightbox-img") {
        closeLightbox();
      }
    },
    true
  );

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeLightbox();
  });
})();
