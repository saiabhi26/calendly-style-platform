// --- Token storage ---
const TOKEN_KEY = "abk_token";
let selectedOrgId = null;

const getToken = () => localStorage.getItem(TOKEN_KEY);
const setToken = (t) => localStorage.setItem(TOKEN_KEY, t);
const clearToken = () => localStorage.removeItem(TOKEN_KEY);

// --- Tiny toast for feedback ---
function toast(message, isError = false) {
  const el = document.getElementById("toast");
  el.textContent = message;
  el.style.background = isError ? "#c0392b" : "#2d8a4e";
  el.hidden = false;
  clearTimeout(toast._t);
  toast._t = setTimeout(() => { el.hidden = true; }, 3000);
}

// --- One fetch helper: attaches JWT, parses JSON, surfaces API errors ---
async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const token = getToken();
  if (token) headers["Authorization"] = "Bearer " + token;

  const res = await fetch(path, { ...options, headers });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch (_) { /* non-JSON error body */ }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  if (res.status === 204) return null;
  return res.json();
}

// --- Auth: register ---
document.getElementById("register-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = new FormData(e.target);
  try {
    await api("/auth/register", {
      method: "POST",
      body: JSON.stringify({
        full_name: f.get("full_name") || null,
        email: f.get("email"),
        password: f.get("password"),
      }),
    });
    toast("Account created — now log in.");
    e.target.reset();
  } catch (err) {
    toast(err.message, true);
  }
});

// --- Auth: login ---
document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = new FormData(e.target);
  try {
    const data = await api("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email: f.get("email"), password: f.get("password") }),
    });
    setToken(data.access_token);
    await showDashboard();
  } catch (err) {
    toast(err.message, true);
  }
});

// --- Auth: logout ---
document.getElementById("logout-btn").addEventListener("click", () => {
  clearToken();
  selectedOrgId = null;
  document.getElementById("dashboard-view").hidden = true;
  document.getElementById("auth-view").hidden = false;
});

// --- Switch to the dashboard (also used on page load if a token exists) ---
async function showDashboard() {
  try {
    const me = await api("/auth/me");
    document.getElementById("user-email").textContent = me.email;
    document.getElementById("auth-view").hidden = true;
    document.getElementById("dashboard-view").hidden = false;
    await loadOrgs();
  } catch (_) {
    // Token missing/expired/invalid — drop it and stay on the auth view.
    clearToken();
  }
}

// --- Organizations ---
async function loadOrgs() {
  const orgs = await api("/organizations");
  const ul = document.getElementById("org-list");
  ul.innerHTML = "";
  if (orgs.length === 0) {
    ul.innerHTML = "<li><em>No organizations yet.</em></li>";
    return;
  }
  orgs.forEach((o) => {
    const li = document.createElement("li");
    li.textContent = `${o.name} (${o.slug})`;
    li.dataset.id = o.id;
    if (o.id === selectedOrgId) li.classList.add("selected");
    li.addEventListener("click", () => selectOrg(o));
    ul.appendChild(li);
  });
}

document.getElementById("org-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = new FormData(e.target);
  try {
    await api("/organizations", {
      method: "POST",
      body: JSON.stringify({
        name: f.get("name"),
        slug: f.get("slug"),
        timezone: f.get("timezone") || "UTC",
      }),
    });
    toast("Organization created.");
    e.target.reset();
    await loadOrgs();
  } catch (err) {
    toast(err.message, true);
  }
});

// --- Services (scoped to the selected org) ---
async function selectOrg(org) {
  selectedOrgId = org.id;
  document.querySelectorAll("#org-list li").forEach((li) =>
    li.classList.toggle("selected", Number(li.dataset.id) === org.id)
  );
  document.getElementById("services-for").textContent = `— ${org.name}`;
  document.getElementById("services-hint").hidden = true;
  document.getElementById("service-create").hidden = false;

  document.getElementById("availability-for").textContent = `— ${org.name}`;
  document.getElementById("availability-hint").hidden = true;
  document.getElementById("availability-body").hidden = false;

  await loadServices();   // also fills the availability service picker
  await loadAvailability();
}

async function loadServices() {
  if (!selectedOrgId) return;
  const services = await api(`/services?organization_id=${selectedOrgId}`);

  // Keep the availability panel's service picker in sync with this org's services
  const availSel = document.getElementById("availability-service");
  const prev = availSel.value;
  availSel.innerHTML = "";
  services.forEach((s) => {
    const opt = document.createElement("option");
    opt.value = s.id;
    opt.textContent = s.title;
    availSel.appendChild(opt);
  });
  if (prev && [...availSel.options].some((o) => o.value === prev)) availSel.value = prev;

  const ul = document.getElementById("service-list");
  ul.innerHTML = "";
  if (services.length === 0) {
    ul.innerHTML = "<li><em>No services yet.</em></li>";
    return;
  }
  services.forEach((s) => {
    const li = document.createElement("li");
    const row = document.createElement("div");
    row.className = "service-row";

    const span = document.createElement("span");
    span.textContent = `${s.title} · ${s.duration_minutes} min · $${s.price} · ${s.mode}`;

    const btn = document.createElement("button");
    btn.textContent = "Delete";
    btn.className = "secondary outline";
    btn.addEventListener("click", () => deleteService(s.id));

    row.append(span, btn);
    li.appendChild(row);
    ul.appendChild(li);
  });
}

document.getElementById("service-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!selectedOrgId) {
    toast("Select an organization first.", true);
    return;
  }
  const f = new FormData(e.target);
  try {
    await api("/services", {
      method: "POST",
      body: JSON.stringify({
        organization_id: selectedOrgId,
        title: f.get("title"),
        duration_minutes: Number(f.get("duration_minutes")),
        price: Number(f.get("price")),
        mode: f.get("mode"),
      }),
    });
    toast("Service created.");
    e.target.reset();
    await loadServices();
  } catch (err) {
    toast(err.message, true);
  }
});

async function deleteService(id) {
  try {
    await api(`/services/${id}`, { method: "DELETE" });
    toast("Service deleted.");
    await loadServices();
  } catch (err) {
    toast(err.message, true);
  }
}

// --- Availability (per service) ---
const DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

async function loadAvailability() {
  const serviceId = document.getElementById("availability-service").value;
  const ul = document.getElementById("availability-list");
  ul.innerHTML = "";
  if (!serviceId) {
    ul.innerHTML = "<li><em>Create a service first to set its availability.</em></li>";
    return;
  }
  const rules = await api(`/availability?service_id=${serviceId}`);
  if (rules.length === 0) {
    ul.innerHTML = "<li><em>No availability set for this service.</em></li>";
    return;
  }
  rules.forEach((r) => {
    const li = document.createElement("li");
    const row = document.createElement("div");
    row.className = "service-row";

    const span = document.createElement("span");
    // start_time / end_time come back as "HH:MM:SS" — show HH:MM
    span.textContent = `${DAY_NAMES[r.day_of_week]} · ${r.start_time.slice(0, 5)}–${r.end_time.slice(0, 5)}`;

    const btn = document.createElement("button");
    btn.textContent = "Delete";
    btn.className = "secondary outline";
    btn.addEventListener("click", () => deleteAvailabilityRule(r.id));

    row.append(span, btn);
    li.appendChild(row);
    ul.appendChild(li);
  });
}

// Reload availability when the chosen service changes
document.getElementById("availability-service").addEventListener("change", loadAvailability);

document.getElementById("availability-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const serviceId = document.getElementById("availability-service").value;
  if (!serviceId) {
    toast("Create a service first.", true);
    return;
  }
  const f = new FormData(e.target);
  try {
    await api("/availability", {
      method: "POST",
      body: JSON.stringify({
        service_id: Number(serviceId),
        day_of_week: Number(f.get("day_of_week")),
        start_time: f.get("start_time"),
        end_time: f.get("end_time"),
      }),
    });
    toast("Availability rule added.");
    e.target.reset();
    await loadAvailability();
  } catch (err) {
    toast(err.message, true);
  }
});

async function deleteAvailabilityRule(id) {
  try {
    await api(`/availability/${id}`, { method: "DELETE" });
    toast("Availability rule deleted.");
    await loadAvailability();
  } catch (err) {
    toast(err.message, true);
  }
}

// --- On page load: if a token is stored, jump straight to the dashboard ---
if (getToken()) showDashboard();
