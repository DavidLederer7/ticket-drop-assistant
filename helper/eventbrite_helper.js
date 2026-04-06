// Optional helper for Eventbrite pages.
// This script only annotates the page and never clicks through checkout.

(function () {
  const STYLE_ID = "senior-cruise-helper-style";
  const BADGE_ID = "senior-cruise-helper-badge";

  if (document.getElementById(BADGE_ID)) {
    return;
  }

  const style = document.createElement("style");
  style.id = STYLE_ID;
  style.textContent = `
    .senior-cruise-helper-target {
      outline: 3px solid #c04a2f !important;
      outline-offset: 3px !important;
      box-shadow: 0 0 0 6px rgba(192, 74, 47, 0.18) !important;
      border-radius: 8px !important;
    }

    #${BADGE_ID} {
      position: fixed;
      right: 16px;
      bottom: 16px;
      z-index: 2147483647;
      max-width: 320px;
      padding: 14px 16px;
      border-radius: 14px;
      background: rgba(18, 33, 47, 0.95);
      color: #fff;
      font: 13px/1.4 -apple-system, BlinkMacSystemFont, sans-serif;
      box-shadow: 0 16px 36px rgba(0, 0, 0, 0.24);
    }

    #${BADGE_ID} code {
      color: #f9c57e;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    }
  `;
  document.head.appendChild(style);

  function firstSelector(selectors) {
    for (const selector of selectors) {
      const node = document.querySelector(selector);
      if (node) {
        return node;
      }
    }
    return null;
  }

  function highlight(node) {
    if (node) {
      node.classList.add("senior-cruise-helper-target");
    }
  }

  function detectState() {
    const text = document.body.innerText.toLowerCase();
    if (text.includes("sales ended") || text.includes("sold out")) {
      return "Sold out or sales ended";
    }
    if (text.includes("enter promo code") || text.includes("access code")) {
      return "Promo code / access code prompt visible";
    }
    if (text.includes("tickets") && (text.includes("register") || text.includes("checkout"))) {
      return "Ticket selection or checkout visible";
    }
    if (text.includes("starts on") || text.includes("sales start")) {
      return "On sale soon";
    }
    if (text.includes("queue") || text.includes("waiting room")) {
      return "Queue or waiting room";
    }
    return "State unclear";
  }

  function renderBadge() {
    const badge = document.createElement("div");
    badge.id = BADGE_ID;
    badge.innerHTML = `
      <strong>Senior Cruise Helper</strong><br>
      State: <span id="senior-cruise-helper-state"></span><br>
      Enter your promo code and UNI in the local dashboard.<br>
      Manual flow: refresh, apply code, choose one ticket, enter UNI if prompted, checkout manually.
    `;
    document.body.appendChild(badge);
    return badge;
  }

  const badge = renderBadge();
  const stateEl = badge.querySelector("#senior-cruise-helper-state");

  function scan() {
    document.querySelectorAll(".senior-cruise-helper-target").forEach((node) => {
      node.classList.remove("senior-cruise-helper-target");
    });

    const promoInput = firstSelector([
      'input[placeholder*="promo" i]',
      'input[aria-label*="promo" i]',
      'input[aria-label*="access code" i]',
    ]);
    const quantityControl = firstSelector([
      'select[name*="quantity" i]',
      'button[aria-label*="quantity" i]',
      'input[type="number"]',
    ]);
    const primaryButton = firstSelector([
      'button[data-testid*="checkout"]',
      'button[aria-label*="checkout" i]',
      'button[aria-label*="register" i]',
      'button[type="submit"]',
    ]);

    highlight(promoInput);
    highlight(quantityControl);
    highlight(primaryButton);
    stateEl.textContent = detectState();
  }

  scan();
  new MutationObserver(scan).observe(document.body, {
    childList: true,
    subtree: true,
    attributes: true,
  });
})();
