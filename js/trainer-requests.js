/* Trainer Panel JS - Candidate Requests Inbox & Priority Filtering */
(() => {
  const el = id => document.getElementById(id);
  let openId = null;

  document.querySelectorAll('.tab').forEach(t => t.onclick = () => {
    document.querySelectorAll('.tab').forEach(x => x.classList.toggle('active', x === t));
    if (el('tabReq')) el('tabReq').classList.toggle('hidden', t.dataset.tab !== 'Req');
    if (el('tabAvail')) el('tabAvail').classList.toggle('hidden', t.dataset.tab !== 'Avail');
  });

  function filtered() {
    const q = el('fSearch').value.toLowerCase().trim(),
          date = el('fDate').value,
          month = el('fMonth').value,
          time = el('fTime').value,
          status = el('fStatus').value,
          sort = el('fSort').value;
    
    let a = getBookings().filter(b => (!q || (b.name + ' ' + b.email + ' ' + b.id).toLowerCase().includes(q)) &&
                                     (!date || b.date === date) &&
                                     (!month || b.date.startsWith(month)) &&
                                     (!time || b.time === time) &&
                                     (!status || b.status === status));
    
    a.sort((x, y) => sort === 'priority' ? priorityOf(y).rank - priorityOf(x).rank || ((priorityOf(y).score ?? -1) - (priorityOf(x).score ?? -1)) :
                    sort === 'slot' ? (x.date + x.time).localeCompare(y.date + y.time) :
                    y.created - x.created);
    return a;
  }

  function renderRequests() {
    if (!el('reqList')) return;
    const all = getBookings(), count = s => all.filter(b => b.status === s).length;
    if (el('cPending')) el('cPending').textContent = count('PENDING_APPROVAL');
    if (el('cAccepted')) el('cAccepted').textContent = count('ACCEPTED');
    if (el('cConfirmed')) el('cConfirmed').textContent = count('CONFIRMED');

    const rows = filtered();
    el('reqList').innerHTML = rows.length ? rows.map(b => {
      const p = priorityOf(b), st = STATUS[b.status] || STATUS.PENDING_FORM;
      return `<div class="summary-top" style="margin-bottom:12px;padding-bottom:12px">
        <div style="flex:1.5">
          <b style="font-size:14px;display:block">${b.name}</b>
          <small style="color:var(--text-muted);font-size:11px">${b.email}</small>
        </div>
        <div style="flex:1.5">
          <b style="font-size:13px;display:block">${prettyDate(b.date)}</b>
          <small style="color:var(--text-muted);font-size:11px">${fmt(b.time)} · ${b.duration} min</small>
        </div>
        <span class="badge ${p.cls}">${p.label}${p.score !== null ? ' · ' + p.score : ''}</span>
        <span class="status ${st.cls}" style="margin-left:8px">${st.label}</span>
        <button class="edit-btn" data-view="${b.id}" style="margin-left:12px">View</button>
      </div>`;
    }).join('') : '<p class="text-muted" style="margin-top:18px;font-size:13px">No requests match the current filters. Use “Load demo requests” to populate the prototype.</p>';
    
    detail();
  }

  function detail() {
    const box = el('reqDetail'), b = openId && getBooking(openId);
    if (!box) return;
    if (!b) {
      box.classList.add('hidden');
      return;
    }
    const p = priorityOf(b), f = b.form;
    box.classList.remove('hidden');
    box.innerHTML = `<div class="section-kicker">REQUEST ${b.id}</div>
    <h2 style="font-size:20px;font-weight:800;margin-bottom:16px">${b.name}</h2>
    <div class="summary-grid" style="margin-bottom:18px">
      <div><small>EMAIL</small><b>${b.email}</b></div>
      <div><small>PHONE</small><b>${b.phone}</b></div>
      <div><small>STATUS</small><b>${(STATUS[b.status] || STATUS.PENDING_FORM).label}</b></div>
      <div><small>PREFERRED DATE</small><b>${prettyDate(b.date)}</b></div>
      <div><small>TIME / DURATION</small><b>${fmt(b.time)} · ${b.duration} min</b></div>
      <div><small>PRIORITY INDICATOR</small><b>${p.label}${p.score !== null ? ' · score ' + p.score : ''}</b></div>
      <div><small>FORM RESPONSE</small><b>${f ? 'Received' : 'Not submitted'}</b></div>
      <div><small>FORM DETAILS</small><b>${f?.notes || '—'}</b></div>
    </div>
    <div class="demo-tag"><b>Prototype note:</b> the priority rule and exact form fields are placeholders until confirmed. The real form response will be integrated here.</div>
    <div class="form-actions" style="margin-top:16px">
      <button class="text-btn" id="closeDet">Close</button>
      <div>
        ${b.status === 'PENDING_APPROVAL' ? `<button class="danger-btn" id="rej">Reject request</button><button class="primary-btn" id="acc" style="margin-left:8px">Accept request</button>` : ''}
      </div>
    </div>`;

    el('closeDet').onclick = () => { openId = null; detail(); };
    if (el('acc')) el('acc').onclick = () => {
      if (acceptedConflict(b.date, b.time, b.duration, b.id)) return alert('This request overlaps an already accepted/confirmed appointment. Choose another request or resolve the existing appointment first.');
      updateBooking(b.id, { status: 'ACCEPTED', acceptedAt: Date.now() });
      openId = null;
      renderRequests();
    };
    if (el('rej')) el('rej').onclick = () => {
      updateBooking(b.id, { status: 'REJECTED', reason: 'The trainer did not accept this request.' });
      openId = null;
      renderRequests();
    };
    box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  if (el('reqList')) {
    el('reqList').onclick = e => {
      if (e.target.dataset.view) {
        openId = e.target.dataset.view;
        detail();
      }
    };
  }

  ['fSearch', 'fDate', 'fMonth', 'fTime', 'fStatus', 'fSort'].forEach(i => {
    if (el(i)) el(i).addEventListener('input', renderRequests);
  });

  if (el('seedBtn')) {
    el('seedBtn').onclick = () => {
      const d = n => {
        const x = new Date();
        x.setDate(x.getDate() + n);
        return localISO(x);
      };
      const mk = (name, n, time, score) => ({
        id: newId(),
        date: d(n),
        time,
        start: time,
        duration: 30,
        name,
        email: name.split(' ')[0].toLowerCase() + '@example.com',
        phone: '9876543210',
        status: 'PENDING_APPROVAL',
        form: { score, notes: 'Demo response' },
        created: Date.now() - Math.floor(Math.random() * 1000000)
      });
      const seeded = [
        mk('Aarav Sharma', 1, '10:00', 86),
        mk('Diya Nair', 1, '10:00', 64),
        mk('Rohan Mehta', 1, '10:00', 42),
        mk('Sneha Iyer', 2, '11:00', 71),
        mk('Karan Patel', 3, '10:30', 55)
      ];
      saveBookings([...getBookings(), ...seeded]);
      seeded.forEach(syncLeadToMarketing);
      renderRequests();
    };
  }

  renderRequests();
})();
