/* Reminder Center JS - Swati Module Integration */
(() => {
  const initialMeetings = [
    { id: 1, title: "Team Meeting", purpose: "Weekly project sync", date: "Today", time: "10:30 AM", participant: "Anika Sharma", phone: "+91 98765 43210", email: "anika@example.com", status: "Accepted" },
    { id: 2, title: "Project Discussion", purpose: "Discuss development progress", date: "Today", time: "2:00 PM", participant: "Rahul Mehta", phone: "+91 91234 56789", email: "rahul@example.com", status: "Accepted" },
    { id: 3, title: "Client Demo", purpose: "Product demonstration", date: "Today", time: "4:30 PM", participant: "Priya Nair", phone: "+91 99887 66554", email: "priya@example.com", status: "Pending" }
  ];

  let meetings = [...initialMeetings];
  
  // Sync confirmed appointments from local bookings if available
  const bookings = getBookings().filter(b => ['ACCEPTED', 'CONFIRMED'].includes(b.status));
  if (bookings.length > 0) {
    const dynamicMeetings = bookings.map((b, idx) => ({
      id: 100 + idx,
      title: b.name + " Appointment",
      purpose: "Appointment Booking",
      date: prettyDate(b.date),
      time: fmt(b.time),
      participant: b.name,
      phone: b.phone,
      email: b.email,
      status: b.status === 'CONFIRMED' ? 'Accepted' : 'Pending'
    }));
    meetings = [...dynamicMeetings, ...meetings];
  }

  let selected = meetings[0], reminder = 15;

  function renderReminders() {
    const listEl = document.getElementById("meetingList");
    const detEl = document.getElementById("details");
    if (!listEl || !detEl) return;

    listEl.innerHTML = meetings.map(m => `
    <button class="slot available ${m.id === selected.id ? "selected" : ""}" style="width:100%;text-align:left;align-items:flex-start;padding:12px 16px;margin-bottom:10px" onclick="selectMeeting(${m.id})">
      <div style="display:flex;justify-content:space-between;width:100%">
        <div>
          <b style="font-size:14px;display:block">${m.title}</b>
          <span style="font-size:12px;color:var(--text-muted);display:block">${m.purpose}</span>
          <small style="font-size:11px;color:var(--text-light);display:block;margin-top:2px">${m.participant} · ${m.phone}</small>
        </div>
        <div style="text-align:right">
          <div style="font-size:13px;font-weight:700">${m.time}</div>
          <small style="font-size:10px;color:var(--text-muted);display:block">${m.date}</small>
          <span class="status ${m.status.toLowerCase()}" style="margin-top:6px">${m.status}</span>
        </div>
      </div>
    </button>`).join("");

    detEl.innerHTML = `
    <div class="stat-card"><label>MEETING</label><strong>${selected.title}</strong><small>${selected.date} · ${selected.time}</small></div>
    <div class="stat-card"><label>PURPOSE</label><strong>${selected.purpose}</strong><small>Meeting purpose</small></div>
    <div class="stat-card"><label>PARTICIPANT</label><strong>${selected.participant}</strong><small>Scheduled participant</small></div>
    <div class="stat-card"><label>PHONE NUMBER</label><strong>${selected.phone}</strong><small>Reminder contact</small></div>
    <div class="stat-card"><label>EMAIL</label><strong>${selected.email}</strong><small>Email contact</small></div>
    <div class="stat-card"><label>REMINDER</label><strong>${format(reminder)}</strong><small>Selected timing</small></div>`;

    if (document.getElementById("selectedStatus")) {
      document.getElementById("selectedStatus").textContent = selected.status;
      document.getElementById("selectedStatus").className = "status " + selected.status.toLowerCase();
    }
  }

  window.selectMeeting = function(id) {
    selected = meetings.find(m => m.id === id) || meetings[0];
    renderReminders();
  };

  function format(v) {
    if (v < 60) return v + " minutes before";
    if (v === 60) return "1 hour before";
    if (v % 1440 === 0) return (v / 1440) + " day" + (v / 1440 > 1 ? "s" : "") + " before";
    return (v / 60) + " hours before";
  }

  function setReminder(v) {
    reminder = Number(v);
    if (document.getElementById("nextReminder")) {
      document.getElementById("nextReminder").textContent = reminder < 60 ? reminder + " min" : (reminder / 60) + " hr";
    }
    renderReminders();
    toast("Reminder set to " + format(reminder));
  }

  if (document.getElementById("timing")) {
    document.getElementById("timing").onchange = e => setReminder(e.target.value);
  }

  window.applyCustom = function() {
    const n = Number(document.getElementById("customValue").value), u = document.getElementById("customUnit").value;
    if (!n || n < 1) {
      toast("Enter a valid custom time");
      return;
    }
    setReminder(u === "minutes" ? n : u === "hours" ? n * 60 : n * 1440);
  };

  function toast(msg) {
    let t = document.getElementById("toast");
    if (!t) {
      t = document.createElement("div");
      t.id = "toast";
      t.className = "toast";
      document.body.appendChild(t);
    }
    t.textContent = msg;
    t.classList.add("show");
    setTimeout(() => t.classList.remove("show"), 2000);
  }

  renderReminders();
})();
