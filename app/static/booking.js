// Read the org slug from the URL (?org=acme); otherwise the slug prompt is shown.
const params = new URLSearchParams(window.location.search);
let orgSlug = params.get("org");

// Booking flow state
let selectedService = null;
let selectedDate = null; // "YYYY-MM-DD"
let selectedSlot = null; // { start, end }

function toast(message, isError = false) {
  const el = document.getElementById("toast");
  el.textContent = message;
  el.style.background = isError ? "#c0392b" : "#2d8a4e";
  el.hidden = false;
  clearTimeout(toast._t);
  toast._t = setTimeout(() => { el.hidden = true; }, 3500);
}

// Public API — no auth token needed for any of these endpoints.
async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const res = await fetch(path, { ...options, headers });
  if (!res.ok) {
    let detail = res.statusText;
    try { detail = (await res.json()).detail ?? detail; } catch (_) {}
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  if (res.status === 204) return null;
  return res.json();
}

function markSelected(container, el) {
  container.querySelectorAll(".chip").forEach((c) => c.classList.remove("selected"));
  if (el) el.classList.add("selected");
}

// --- Load org + its services ---
async function loadOrg(slug) {
  try {
    const org = await api(`/orgs/${slug}`);
    document.getElementById("org-name").textContent = org.name;
    document.getElementById("org-tagline").textContent = "Book an appointment";
    document.getElementById("slug-prompt").hidden = true;
    document.getElementById("booking-flow").hidden = false;
    orgSlug = slug;
    await loadServices(slug);
  } catch (err) {
    toast(err.message, true);
  }
}

async function loadServices(slug) {
  const services = await api(`/orgs/${slug}/services`);
  const wrap = document.getElementById("service-list");
  wrap.innerHTML = "";
  if (services.length === 0) {
    wrap.innerHTML = "<p><em>This business has no services yet.</em></p>";
    return;
  }
  services.forEach((s) => {
    const chip = document.createElement("button");
    chip.className = "chip";
    chip.textContent = `${s.title} · ${s.duration_minutes} min · $${s.price}`;
    chip.addEventListener("click", () => selectService(s, chip));
    wrap.appendChild(chip);
  });
}

// --- Step 1 -> 2: pick a service, reveal the day picker ---
function selectService(svc, chipEl) {
  selectedService = svc;
  selectedSlot = null;
  markSelected(document.getElementById("service-list"), chipEl);
  document.getElementById("day-section").hidden = false;
  document.getElementById("slot-section").hidden = true;
  document.getElementById("details-section").hidden = true;
  renderDays();
}

// --- Step 2: show only the next-14 days the org is actually open ---
async function renderDays() {
  const wrap = document.getElementById("day-list");
  wrap.innerHTML = "";

  let openDays;
  try {
    // Weekdays this service has availability for: 0=Mon … 6=Sun (Python convention)
    openDays = new Set(await api(`/orgs/${orgSlug}/services/${selectedService.id}/available-days`));
  } catch (err) {
    toast(err.message, true);
    return;
  }
  if (openDays.size === 0) {
    wrap.innerHTML = "<p><em>This business hasn't set any availability yet.</em></p>";
    return;
  }

  const fmt = new Intl.DateTimeFormat(undefined, { weekday: "short", month: "short", day: "numeric" });
  let shown = 0;
  for (let i = 0; i < 14; i++) {
    const d = new Date();
    d.setDate(d.getDate() + i);
    // JS getDay(): Sun=0 … Sat=6  ->  Python weekday(): Mon=0 … Sun=6
    const pyWeekday = (d.getDay() + 6) % 7;
    if (!openDays.has(pyWeekday)) continue; // skip closed days

    // Build YYYY-MM-DD from local parts (avoids UTC off-by-one from toISOString)
    const value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
    const chip = document.createElement("button");
    chip.className = "chip";
    chip.textContent = i === 0 ? "Today" : fmt.format(d);
    chip.addEventListener("click", () => selectDay(value, chip));
    wrap.appendChild(chip);
    shown++;
  }
  if (shown === 0) {
    wrap.innerHTML = "<p><em>No open days in the next two weeks.</em></p>";
  }
}

// --- Step 2 -> 3: pick a day, fetch its open slots ---
async function selectDay(dateStr, chipEl) {
  selectedDate = dateStr;
  selectedSlot = null;
  markSelected(document.getElementById("day-list"), chipEl);
  document.getElementById("slot-section").hidden = false;
  document.getElementById("details-section").hidden = true;
  await loadSlots();
}

async function loadSlots() {
  const wrap = document.getElementById("slot-list");
  const noSlots = document.getElementById("no-slots");
  wrap.innerHTML = "";
  noSlots.hidden = true;
  try {
    const slots = await api(`/slots?service_id=${selectedService.id}&date=${selectedDate}`);
    if (slots.length === 0) {
      noSlots.hidden = false;
      return;
    }
    slots.forEach((slot) => {
      const chip = document.createElement("button");
      chip.className = "chip";
      chip.textContent = slot.start.substring(11, 16); // HH:MM wall-clock (org timezone)
      chip.addEventListener("click", () => selectSlot(slot, chip));
      wrap.appendChild(chip);
    });
  } catch (err) {
    toast(err.message, true);
  }
}

// --- Step 3 -> 4: pick a time, reveal the details form ---
function selectSlot(slot, chipEl) {
  selectedSlot = slot;
  markSelected(document.getElementById("slot-list"), chipEl);
  document.getElementById("details-section").hidden = false;
}

// --- Step 4: submit the booking ---
document.getElementById("booking-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!selectedSlot) {
    toast("Pick a time first.", true);
    return;
  }
  const f = new FormData(e.target);
  try {
    const booking = await api("/bookings", {
      method: "POST",
      body: JSON.stringify({
        service_id: selectedService.id,
        slot_start: selectedSlot.start,
        customer_name: f.get("customer_name"),
        customer_email: f.get("customer_email"),
      }),
    });
    showConfirmation(booking);
  } catch (err) {
    toast(err.message, true);
    // If the slot was taken between viewing and booking, refresh this day's slots.
    if (/booked|available/i.test(err.message)) loadSlots();
  }
});

function showConfirmation(booking) {
  document.getElementById("booking-flow").hidden = true;
  const conf = document.getElementById("confirmation");
  conf.hidden = false;
  const when = `${selectedDate} at ${booking.slot_start.substring(11, 16)}`;
  document.getElementById("confirmation-detail").textContent =
    `${selectedService.title} on ${when}. We'll send a confirmation to ${booking.customer_email}.`;
}

document.getElementById("book-another").addEventListener("click", () => {
  selectedService = selectedDate = selectedSlot = null;
  document.getElementById("confirmation").hidden = true;
  document.getElementById("booking-flow").hidden = false;
  document.getElementById("day-section").hidden = true;
  document.getElementById("slot-section").hidden = true;
  document.getElementById("details-section").hidden = true;
  markSelected(document.getElementById("service-list"), null);
});

// --- Slug prompt (used when the page is opened without ?org=) ---
document.getElementById("slug-go").addEventListener("click", () => {
  const slug = document.getElementById("slug-input").value.trim();
  if (slug) loadOrg(slug);
});
document.getElementById("slug-input").addEventListener("keydown", (e) => {
  if (e.key === "Enter") document.getElementById("slug-go").click();
});

// --- Auto-load if the org slug is in the URL ---
if (orgSlug) loadOrg(orgSlug);
