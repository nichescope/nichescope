// NicheScope frontend — vanilla JS, talks to the FastAPI /api/analyze endpoint.
const $ = (s) => document.querySelector(s);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const money = (n) => "$" + Number(n).toFixed(2);

async function analyze(keyword) {
  $("#empty").classList.add("hidden");
  $("#error").classList.add("hidden");
  $("#report").classList.add("hidden");

  const res = await fetch(`/api/analyze?keyword=${encodeURIComponent(keyword)}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    $("#error").textContent = err.error || `Request failed (${res.status}).`;
    $("#error").classList.remove("hidden");
    return;
  }
  render(await res.json());
}

function render(r) {
  $("#k-count").textContent = r.total_count.toLocaleString();
  const comp = $("#k-comp");
  comp.textContent = r.competition;
  comp.className = "k-val comp-" + r.competition;
  $("#k-median").textContent = money(r.price.median);
  $("#k-favs").textContent = r.favorites.avg.toLocaleString();

  $("#price-range").textContent = `${money(r.price.min)} – ${money(r.price.max)} · avg ${money(r.price.avg)}`;

  const maxCount = Math.max(...r.histogram.map((h) => h.count), 1);
  $("#hist").innerHTML = r.histogram.map((h) => `
    <div class="bar-col" title="${h.label}: ${h.count} listings">
      <div class="bar-fill" style="height:${(h.count / maxCount) * 100}%"></div>
      <div class="bar-x">${esc(h.label)}</div>
    </div>`).join("");

  $("#tags").innerHTML = r.top_tags.map((t) =>
    `<span class="tag">${esc(t.tag)} <span class="n">${t.count}</span></span>`).join("")
    || `<span class="muted">No tags found.</span>`;

  
  // Optional shop velocity (only when backend enabled it)
  const velBox = $("#velocity");
  if (velBox) {
    const vel = r.shop_velocity || {};
    const shops = Object.keys(vel);
    if (!r.velocity_enabled || !shops.length) {
      velBox.classList.add("hidden");
      velBox.innerHTML = "";
    } else {
      velBox.classList.remove("hidden");
      velBox.innerHTML = "<h2>Shop velocity (30d)</h2><div class=\"tags\">" + shops.map((s) => {
        const v = vel[s] || {};
        const sales = v.sales_30d ?? v.delta_28d;
        const trend = v.breakout ? "breakout" : (v.status === "no_coverage" ? "n/a" : "ok");
        const label = sales == null ? "n/a" : String(sales);
        return `<span class="tag">${esc(s)} <span class="n">${esc(label)} · ${esc(trend)}</span></span>`;
      }).join("") + "</div>";
    }
  }

  $("#report").classList.remove("hidden");
}

$("#form").addEventListener("submit", (e) => {
  e.preventDefault();
  const kw = $("#kw").value.trim();
  if (kw) analyze(kw);
});

// prefill a demo query so the page isn't empty on first load
window.addEventListener("DOMContentLoaded", () => {
  $("#kw").value = "dog mom mug";
  analyze("dog mom mug");
});
