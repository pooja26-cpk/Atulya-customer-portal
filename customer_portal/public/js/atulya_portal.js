const titles = {
  dashboard: 'Dashboard', orders: 'Sales Orders',
  invoices: 'Invoices', payments: 'Payments',
  ledger: 'Ledger', support: 'Support', profile: 'My Profile'
};

function showPage(id, navEl) { 
    // Basic navigation logic stub
    console.log("Navigating to", id);
}

// Runs when Frappe's DOM is ready
frappe.ready(async function() {
  // Dashboard data is now loaded purely via Jinja in portal.py
  console.log("Dashboard loaded via Jinja!");
});

// ── Helpers ───────────────────────────────────────────
function inr(id, v) {
  setText(id, "₹" + Number(v||0).toLocaleString("en-IN"));
}
function pct(id, v) {
  setText(id, (v||0).toFixed(1) + "%");
}
function bar(id, v) {
  const el = document.getElementById(id);
  if(el) el.style.width = Math.min(v||0, 100) + "%";
}
function setText(id, val) {
  const el = document.getElementById(id);
  if(el) el.textContent = val;
}

// ── Render Functions ──────────────────────────────────
// (Table rendering logic removed since it is handled by Jinja)
