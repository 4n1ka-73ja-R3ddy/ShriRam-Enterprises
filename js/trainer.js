/* Trainer Panel JS - Schedule & Availability Management */
const $ = id => document.getElementById(id);
let avail = getAvail();
const today = localISO(new Date());

if ($("day")) $("day").innerHTML = WEEK_ORDER.map(d => `<option>${d}</option>`).join("");
if ($("leaveDate")) $("leaveDate").min = today;

const persist = () => write(KEYS.availability, avail);
function flash(id) { const m = $(id); if (m) { m.classList.remove("hidden"); setTimeout(() => m.classList.add("hidden"), 2200); } }
function showError(id, msg) { const e = $(id); if (e) { e.textContent = msg || ""; e.classList.toggle("hidden", !msg); } }

function renderSchedule() {
  if (!$("schedule")) return;
  $("schedule").innerHTML = WEEK_ORDER.map(day => {
    const w = avail.weekly[day], on = w.on, cls = on ? "available" : "unavailable";
    return `<div class="summary-top" style="margin-bottom:12px;padding-bottom:12px">
      <div style="flex:1"><b style="font-size:15px">${day}</b></div>
      <div style="flex:2;color:var(--text-muted);font-size:13px">${on ? fmt(w.start) + " – " + fmt(w.end) : "No availability set"}</div>
      <span class="status ${cls}">${on ? "Available" : "Unavailable"}</span>
      <button class="edit-btn" data-day="${day}" style="margin-left:12px">Edit</button>
    </div>`;
  }).join("");

  avail.leaves = avail.leaves.filter(l => l.date >= today).sort((a, b) => a.date.localeCompare(b.date));
  if ($("leaveList")) {
    $("leaveList").innerHTML = avail.leaves.length
      ? avail.leaves.map((l, i) => `<div class="summary-top" style="margin-bottom:12px;padding-bottom:12px">
          <div style="flex:1"><b style="font-size:14px">${prettyDate(l.date)}</b></div>
          <div style="flex:2;color:var(--text-muted);font-size:13px">${l.start ? fmt(l.start) + " – " + fmt(l.end) : "Whole day"}</div>
          <span class="status unavailable">${l.reason || 'Leave'}</span>
          <button class="edit-btn" data-remove="${i}" style="margin-left:12px">Remove</button>
        </div>`).join("")
      : '<p class="text-muted" style="margin-top:12px;font-size:13px">No unavailable dates marked.</p>';
  }

  const onCount = WEEK_ORDER.filter(d => avail.weekly[d].on).length;
  if ($("availableCount")) $("availableCount").textContent = onCount;
  if ($("unavailableCount")) $("unavailableCount").textContent = 7 - onCount;
  if ($("leaveCount")) $("leaveCount").textContent = avail.leaves.length;
}

function toggleTimeFields() {
  if (!$("status")) return;
  const off = $("status").value === "unavailable";
  if ($("start")) $("start").disabled = off;
  if ($("end")) $("end").disabled = off;
}

if ($("schedule")) {
  $("schedule").addEventListener("click", e => {
    const day = e.target.dataset.day; if (!day) return;
    const w = avail.weekly[day];
    $("day").value = day;
    $("status").value = w.on ? "available" : "unavailable";
    $("start").value = w.start || "10:00";
    $("end").value = w.end || "13:00";
    toggleTimeFields();
    showError("weeklyError");
    $("day").scrollIntoView({ behavior: "smooth", block: "center" });
  });
}

if ($("status")) $("status").addEventListener("change", toggleTimeFields);

if ($("saveBtn")) {
  $("saveBtn").addEventListener("click", () => {
    const day = $("day").value, on = $("status").value === "available", start = $("start").value, end = $("end").value;
    if (on && (!start || !end)) return showError("weeklyError", "Please enter both start and end time.");
    if (on && toMin(start) >= toMin(end)) return showError("weeklyError", "End time must be after start time.");
    avail.weekly[day] = on ? { on, start, end } : { on: false };
    persist();
    showError("weeklyError");
    renderSchedule();
    flash("weeklyMsg");
  });
}

if ($("leaveBtn")) {
  $("leaveBtn").addEventListener("click", () => {
    const date = $("leaveDate").value, start = $("leaveStart").value, end = $("leaveEnd").value;
    if (!date) return showError("leaveError", "Please choose a date.");
    if (date < today) return showError("leaveError", "You can't mark a past date.");
    if (!!start !== !!end) return showError("leaveError", "Enter both From and To, or leave both empty for the whole day.");
    if (start && toMin(start) >= toMin(end)) return showError("leaveError", "'To' time must be after 'From' time.");
    avail.leaves.push({ date, start, end, reason: $("leaveReason").value });
    persist();
    showError("leaveError");
    renderSchedule();
    flash("leaveMsg");
    $("leaveStart").value = $("leaveEnd").value = "";
  });
}

if ($("leaveList")) {
  $("leaveList").addEventListener("click", e => {
    const i = e.target.dataset.remove; if (i === undefined) return;
    avail.leaves.splice(+i, 1);
    persist();
    renderSchedule();
  });
}

if ($("resetBtn")) {
  $("resetBtn").addEventListener("click", () => {
    if (!confirm("Reset availability and all demo bookings?")) return;
    resetDemo();
    location.reload();
  });
}

toggleTimeFields();
renderSchedule();
