/* trainer.js - Trainer panel: view / set / modify / mark unavailable */
const $ = id => document.getElementById(id);
let avail = getAvail();
const today = localISO(new Date());

$("day").innerHTML = WEEK_ORDER.map(d => `<option>${d}</option>`).join("");
$("leaveDate").min = today;

const persist = () => write(KEYS.avail, avail);
function flash(id) { const m = $(id); m.classList.remove("hidden"); setTimeout(() => m.classList.add("hidden"), 2200); }
function showError(id, msg) { const e = $(id); e.textContent = msg || ""; e.classList.toggle("hidden", !msg); }

function render() {
  // weekly schedule
  $("schedule").innerHTML = WEEK_ORDER.map(day => {
    const w = avail.weekly[day], on = w.on, cls = on ? "available" : "unavailable";
    return `<div class="schedule-row">
      <div class="day-block"><span class="day-dot ${cls}"></span><b>${day}</b></div>
      <div class="time-block">${on ? fmt(w.start) + " – " + fmt(w.end) : "No availability set"}</div>
      <span class="status ${cls}">${on ? "Available" : "Unavailable"}</span>
      <button class="edit-btn" data-day="${day}">Edit</button></div>`;
  }).join("");

  // upcoming unavailable dates
  avail.leaves = avail.leaves.filter(l => l.date >= today).sort((a, b) => a.date.localeCompare(b.date));
  $("leaveList").innerHTML = avail.leaves.length
    ? avail.leaves.map((l, i) => `<div class="schedule-row">
        <div class="day-block"><span class="day-dot unavailable"></span><b>${prettyDate(l.date)}</b></div>
        <div class="time-block">${l.start ? fmt(l.start) + " – " + fmt(l.end) : "Whole day"}</div>
        <span class="status unavailable">${l.reason}</span>
        <button class="edit-btn" data-remove="${i}">Remove</button></div>`).join("")
    : '<p class="muted" style="margin-top:18px">No unavailable dates marked.</p>';

  const on = WEEK_ORDER.filter(d => avail.weekly[d].on).length;
  $("availableCount").textContent = on;
  $("unavailableCount").textContent = 7 - on;
  $("leaveCount").textContent = avail.leaves.length;
}

function toggleTimeFields() {
  const off = $("status").value === "unavailable";
  $("start").disabled = $("end").disabled = off;
}

$("schedule").addEventListener("click", e => {
  const day = e.target.dataset.day; if (!day) return;
  const w = avail.weekly[day];
  $("day").value = day; $("status").value = w.on ? "available" : "unavailable";
  $("start").value = w.start || "10:00"; $("end").value = w.end || "13:00";
  toggleTimeFields(); showError("weeklyError");
  $("day").scrollIntoView({ behavior: "smooth", block: "center" });
});
$("status").addEventListener("change", toggleTimeFields);

$("saveBtn").addEventListener("click", () => {
  const day = $("day").value, on = $("status").value === "available", start = $("start").value, end = $("end").value;
  if (on && (!start || !end)) return showError("weeklyError", "Please enter both start and end time.");
  if (on && toMin(start) >= toMin(end)) return showError("weeklyError", "End time must be after start time.");
  avail.weekly[day] = on ? { on, start, end } : { on: false };
  persist(); showError("weeklyError"); render(); flash("weeklyMsg");
});

$("leaveBtn").addEventListener("click", () => {
  const date = $("leaveDate").value, start = $("leaveStart").value, end = $("leaveEnd").value;
  if (!date) return showError("leaveError", "Please choose a date.");
  if (date < today) return showError("leaveError", "You can't mark a past date.");
  if (!!start !== !!end) return showError("leaveError", "Enter both From and To, or leave both empty for the whole day.");
  if (start && toMin(start) >= toMin(end)) return showError("leaveError", "'To' time must be after 'From' time.");
  avail.leaves.push({ date, start, end, reason: $("leaveReason").value });
  persist(); showError("leaveError"); render(); flash("leaveMsg");
  $("leaveStart").value = $("leaveEnd").value = "";
});

$("leaveList").addEventListener("click", e => {
  const i = e.target.dataset.remove; if (i === undefined) return;
  avail.leaves.splice(+i, 1); persist(); render();
});

$("resetBtn").addEventListener("click", () => {
  if (!confirm("Reset availability and all demo bookings?")) return;
  localStorage.removeItem(KEYS.avail); localStorage.removeItem(KEYS.bookings);
  location.reload();
});

toggleTimeFields(); render();
