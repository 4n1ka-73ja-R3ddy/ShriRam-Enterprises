/* Appointment System Unified Master Shared Script
   Handles storage, slot availability calculations, booking CRUD, marketing attribution cross-sync, and status transitions.
*/
const KEYS = {
  availability: 'ah_availability_v2',
  bookings: 'ah_bookings_v2',
  selected: 'ah_selected_v2',
  marketing: 'ah_marketing_v2'
};

const DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const WEEK_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

const CONFIG = {
  EXTERNAL_FORM_URL: '', // Real external form URL placeholder
  PAYMENT_AMOUNT: 100
};

const STATUS = {
  PENDING_FORM: { label: 'Form pending', cls: 'pending' },
  PENDING_APPROVAL: { label: 'Awaiting trainer', cls: 'pending' },
  ACCEPTED: { label: 'Payment pending', cls: 'accepted' },
  CONFIRMED: { label: 'Confirmed', cls: 'confirmed' },
  REJECTED: { label: 'Rejected', cls: 'rejected' },
  CANCELLED: { label: 'Cancelled', cls: 'rejected' },
  EXPIRED: { label: 'Expired', cls: 'rejected' }
};

const DEFAULT_AVAIL = {
  weekly: {
    Monday: { on: true, start: '10:00', end: '13:00' },
    Tuesday: { on: true, start: '10:00', end: '13:00' },
    Wednesday: { on: false },
    Thursday: { on: true, start: '14:00', end: '17:00' },
    Friday: { on: true, start: '10:00', end: '13:00' },
    Saturday: { on: false },
    Sunday: { on: false }
  },
  leaves: []
};

// Storage Utilities
function read(key, fallback) {
  try {
    const v = JSON.parse(localStorage.getItem(key));
    return v ?? fallback;
  } catch {
    return fallback;
  }
}

function write(key, val) {
  localStorage.setItem(key, JSON.stringify(val));
}

function clone(x) {
  return JSON.parse(JSON.stringify(x));
}

function getAvail() {
  return read(KEYS.availability, clone(DEFAULT_AVAIL));
}

function getBookings() {
  return read(KEYS.bookings, []);
}

function saveBookings(v) {
  write(KEYS.bookings, v);
}

function getBooking(id) {
  return getBookings().find(b => b.id === id);
}

function updateBooking(id, patch) {
  const a = getBookings();
  const i = a.findIndex(b => b.id === id);
  if (i < 0) return null;
  a[i] = { ...a[i], ...patch };
  saveBookings(a);
  
  // Cross-sync status update to Marketing Lead if exists
  syncLeadStatus(a[i]);
  
  return a[i];
}

function newId() {
  return 'AH-' + Math.random().toString(36).slice(2, 7).toUpperCase() + '-' + Date.now().toString().slice(-4);
}

// Time & Date Helpers
function toMin(t) {
  const [h, m] = t.split(':').map(Number);
  return h * 60 + m;
}

function toTime(m) {
  return String(Math.floor(m / 60)).padStart(2, '0') + ':' + String(m % 60).padStart(2, '0');
}

function fmt(t) {
  if (!t) return '';
  const [h, m] = t.split(':').map(Number);
  return ((h % 12) || 12) + ':' + String(m).padStart(2, '0') + ' ' + (h >= 12 ? 'PM' : 'AM');
}

function localISO(d) {
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
}

function dayOf(iso) {
  return DAYS[new Date(iso + 'T00:00:00').getDay()];
}

function prettyDate(iso) {
  if (!iso) return '';
  return new Date(iso + 'T00:00:00').toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' });
}

function monthLabel(iso) {
  if (!iso) return '';
  return new Date(iso + 'T00:00:00').toLocaleDateString('en-IN', { month: 'long', year: 'numeric' });
}

function overlaps(aStart, aDuration, bStart, bDuration) {
  return toMin(aStart) < toMin(bStart) + bDuration && toMin(bStart) < toMin(aStart) + aDuration;
}

function acceptedConflict(date, time, duration, ignoreId = '') {
  return getBookings().some(b => b.id !== ignoreId && b.date === date && ['ACCEPTED', 'CONFIRMED'].includes(b.status) && overlaps(time, duration, b.time, b.duration));
}

function priorityOf(b) {
  const score = Number(b.form?.score);
  if (!Number.isFinite(score)) return { label: 'Not scored', cls: 'none', rank: -1, score: null };
  if (score >= 75) return { label: 'High', cls: 'high', rank: 3, score };
  if (score >= 50) return { label: 'Medium', cls: 'medium', rank: 2, score };
  return { label: 'Low', cls: 'low', rank: 1, score };
}

function getSlots(iso, duration) {
  const a = getAvail(), w = a.weekly[dayOf(iso)];
  if (!w || !w.on) return [];
  const leaves = a.leaves.filter(l => l.date === iso), bookings = getBookings().filter(b => b.date === iso);
  const now = new Date(), today = iso === localISO(now), nowMin = now.getHours() * 60 + now.getMinutes();
  const out = [];
  
  for (let s = toMin(w.start); s + duration <= toMin(w.end); s += duration) {
    if (today && s <= nowMin) continue;
    const e = s + duration, clash = (x, y) => s < y && x < e;
    let status = 'available';
    if (bookings.some(b => ['ACCEPTED', 'CONFIRMED'].includes(b.status) && clash(toMin(b.time), toMin(b.time) + b.duration))) status = 'booked';
    else if (leaves.some(l => !l.start || clash(toMin(l.start), toMin(l.end)))) status = 'unavailable';
    else if (bookings.some(b => b.status === 'PENDING_FORM' || b.status === 'PENDING_APPROVAL')) status = 'requested';
    out.push({ time: toTime(s), status });
  }
  return out;
}

function resetDemo() {
  localStorage.removeItem(KEYS.availability);
  localStorage.removeItem(KEYS.bookings);
  localStorage.removeItem(KEYS.selected);
  localStorage.removeItem(KEYS.marketing);
}

/* Cross-Module Integration Helpers */
function syncLeadToMarketing(booking) {
  const marketingData = read(KEYS.marketing, { leads: [], visits: [] });
  const existingIndex = marketingData.leads.findIndex(l => l.email === booking.email);
  const leadObj = {
    id: booking.id,
    name: booking.name,
    email: booking.email,
    phone: booking.phone,
    status: booking.status === 'CONFIRMED' ? 'booked' : booking.status === 'ACCEPTED' ? 'qualified' : 'new',
    created_at: new Date().toISOString()
  };
  
  if (existingIndex >= 0) {
    marketingData.leads[existingIndex] = { ...marketingData.leads[existingIndex], ...leadObj };
  } else {
    marketingData.leads.push(leadObj);
  }
  write(KEYS.marketing, marketingData);
}

function syncLeadStatus(booking) {
  const marketingData = read(KEYS.marketing, { leads: [], visits: [] });
  const lead = marketingData.leads.find(l => l.email === booking.email || l.id === booking.id);
  if (lead) {
    lead.status = booking.status === 'CONFIRMED' ? 'booked' : ['ACCEPTED', 'PENDING_APPROVAL'].includes(booking.status) ? 'qualified' : 'new';
    write(KEYS.marketing, marketingData);
  }
}
