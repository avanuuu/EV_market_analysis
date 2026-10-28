/**
 * static/js/main.js
 * =================
 * Client-side interactivity for the Electric Vehicle Market Analysis platform.
 * Handles Tableau dashboard view switching, dynamic filter controls,
 * and data interactions.
 */

document.addEventListener("DOMContentLoaded", function () {
  console.log("EV Market Analysis Intelligence Platform loaded.");

  // Tableau Dashboard View Switching
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tableauFrame = document.getElementById("tableauDashboardFrame");

  if (tabButtons.length > 0 && tableauFrame) {
    tabButtons.forEach(button => {
      button.addEventListener("click", function () {
        tabButtons.forEach(btn => btn.classList.remove("active"));
        this.classList.add("active");

        const targetView = this.getAttribute("data-view");
        const baseUrl = this.getAttribute("data-base-url");

        if (baseUrl && targetView) {
          // Construct URL for specific dashboard sheet
          const newUrl = `${baseUrl}/${targetView}?:embed=yes&:showVizHome=no&:toolbar=yes`;
          tableauFrame.src = newUrl;
          console.log(`Switched Tableau Dashboard View to: ${targetView}`);
        }
      });
    });
  }

  // Auto-dismiss alert banners if any
  const alerts = document.querySelectorAll(".alert-dismissible");
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = "0";
      setTimeout(() => alert.remove(), 400);
    }, 6000);
  });
});

/**
 * Copies text snippet to clipboard and shows feedback.
 */
function copyToClipboard(elementId, btnElement) {
  const codeBlock = document.getElementById(elementId);
  if (!codeBlock) return;
  const text = codeBlock.innerText || codeBlock.textContent;

  navigator.clipboard.writeText(text).then(() => {
    const originalText = btnElement.innerText;
    btnElement.innerText = "Copied!";
    btnElement.classList.add("btn-success");
    setTimeout(() => {
      btnElement.innerText = originalText;
      btnElement.classList.remove("btn-success");
    }, 2000);
  }).catch(err => {
    console.error("Clipboard copy failed:", err);
  });
}
