(function () {
  "use strict";

  var storageKey = "vhp-sponsor-popup-dismissed";
  var popup;

  function dismiss() {
    if (!popup) {
      return;
    }
    popup.hidden = true;
    try {
      window.sessionStorage.setItem(storageKey, "1");
    } catch (error) {
      // Private browsing can disable sessionStorage; hiding still works.
    }
  }

  function createPopup() {
    try {
      if (window.sessionStorage.getItem(storageKey) === "1") {
        return;
      }
    } catch (error) {
      // Continue without persistence when storage is unavailable.
    }

    popup = document.createElement("aside");
    popup.className = "vhp-sponsor-popup";
    popup.setAttribute("aria-labelledby", "vhp-sponsor-title");
    popup.setAttribute("role", "complementary");
    popup.innerHTML =
      '<button class="vhp-sponsor-popup-close" type="button" aria-label="Close sponsor message">&times;</button>' +
      '<h2 id="vhp-sponsor-title">Support VHP open source</h2>' +
      "<p>If these Python projects and learning docs help you, sponsorship helps me keep improving them and building new tools for Python developers.</p>" +
      '<div class="vhp-sponsor-popup-actions">' +
      '<a href="https://github.com/sponsors/Veeresh-Hanni" target="_blank" rel="noopener noreferrer">GitHub Sponsors</a>' +
      '<a href="https://razorpay.me/@veereshhanni" target="_blank" rel="noopener noreferrer">Razorpay</a>' +
      '<button class="vhp-sponsor-popup-dismiss" type="button">Maybe later</button>' +
      "</div>";

    popup.querySelector(".vhp-sponsor-popup-close").addEventListener("click", dismiss);
    popup.querySelector(".vhp-sponsor-popup-dismiss").addEventListener("click", dismiss);
    document.body.appendChild(popup);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", createPopup);
  } else {
    createPopup();
  }
})();
