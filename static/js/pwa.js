(() => {
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("/service-worker.js");
    });
  }

  const installButton = document.querySelector("[data-install-app]");
  const installSheet = document.querySelector("[data-install-sheet]");
  const closeButtons = document.querySelectorAll("[data-close-install]");
  const standalone =
    window.matchMedia("(display-mode: standalone)").matches ||
    window.navigator.standalone === true;

  if (!installButton || standalone) {
    if (installButton) {
      installButton.hidden = true;
    }
    return;
  }

  installButton.addEventListener("click", () => {
    installSheet.hidden = false;
    document.body.classList.add("install-sheet-open");
  });

  closeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      installSheet.hidden = true;
      document.body.classList.remove("install-sheet-open");
    });
  });
})();
