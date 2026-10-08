/* AppointmentHub frontend prototype
   IMPORTANT: localStorage is only a demo stand-in for the future backend/database.
*/
const KEYS = { availability:'ah_availability_v2', bookings:'ah_bookings_v2', selected:'ah_selected_v2' };
const DAYS = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
const WEEK_ORDER = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
const CONFIG = {
  EXTERNAL_FORM_URL: '', // Paste teammate's real form URL here when provided.
  PAYMENT_AMOUNT: 100 // Demo amount only; confirm actual fee with ma'am.
};
const STATUS = {
  PENDING_FORM:{label:'Form pending',cls:'pending'},
  PENDING_APPROVAL:{label:'Awaiting trainer',cls:'pending'},
  ACCEPTED:{label:'Payment pending',cls:'accepted'},
  CONFIRMED:{label:'Confirmed',cls:'confirmed'},
  REJECTED:{label:'Rejected',cls:'rejected'},
  CANCELLED:{label:'Cancelled',cls:'rejected'},
  EXPIRED:{label:'Expired',cls:'rejected'}
};
const DEFAULT_AVAIL = {weekly:{
  Monday:{on:true,start:'10:00',end:'13:00'}, Tuesday:{on:true,start:'10:00',end:'13:00'},
  Wednesday:{on:false}, Thursday:{on:true,start:'14:00',end:'17:00'}, Friday:{on:true,start:'10:00',end:'13:00'},
  Saturday:{on:false}, Sunday:{on:false}
}, leaves:[]};
function read(key,fallback){try{const v=JSON.parse(localStorage.getItem(key));return v??fallback}catch{return fallback}}
function write(key,val){localStorage.setItem(key,JSON.stringify(val))}
function clone(x){return JSON.parse(JSON.stringify(x))}
function getAvail(){return read(KEYS.availability,clone(DEFAULT_AVAIL))}
function getBookings(){return read(KEYS.bookings,[])}
function saveBookings(v){write(KEYS.bookings,v)}
function getBooking(id){return getBookings().find(b=>b.id===id)}
function updateBooking(id,patch){const a=getBookings();const i=a.findIndex(b=>b.id===id);if(i<0)return null;a[i]={...a[i],...patch};saveBookings(a);return a[i]}
function newId(){return 'AH-'+Math.random().toString(36).slice(2,7).toUpperCase()+'-'+Date.now().toString().slice(-4)}
function toMin(t){const [h,m]=t.split(':').map(Number);return h*60+m}
function toTime(m){return String(Math.floor(m/60)).padStart(2,'0')+':'+String(m%60).padStart(2,'0')}
function fmt(t){const [h,m]=t.split(':').map(Number);return ((h%12)||12)+':'+String(m).padStart(2,'0')+' '+(h>=12?'PM':'AM')}
function localISO(d){return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')}
function dayOf(iso){return DAYS[new Date(iso+'T00:00:00').getDay()]}
function prettyDate(iso){return new Date(iso+'T00:00:00').toLocaleDateString('en-IN',{day:'numeric',month:'long',year:'numeric'})}
function monthLabel(iso){return new Date(iso+'T00:00:00').toLocaleDateString('en-IN',{month:'long',year:'numeric'})}
function overlaps(aStart,aDuration,bStart,bDuration){return toMin(aStart)<toMin(bStart)+bDuration && toMin(bStart)<toMin(aStart)+aDuration}
function acceptedConflict(date,time,duration,ignoreId=''){return getBookings().some(b=>b.id!==ignoreId&&b.date===date&&['ACCEPTED','CONFIRMED'].includes(b.status)&&overlaps(time,duration,b.time,b.duration))}
function priorityOf(b){
  // DEMO ONLY: score is displayed as a priority indicator until ma'am confirms the real rule.
  const score=Number(b.form?.score); if(!Number.isFinite(score))return {label:'Not scored',cls:'none',rank:-1,score:null};
  if(score>=75)return {label:'High',cls:'high',rank:3,score};
  if(score>=50)return {label:'Medium',cls:'medium',rank:2,score};
  return {label:'Low',cls:'low',rank:1,score};
}
function getSlots(iso,duration){
  const a=getAvail(),w=a.weekly[dayOf(iso)]; if(!w||!w.on)return [];
  const leaves=a.leaves.filter(l=>l.date===iso), bookings=getBookings().filter(b=>b.date===iso);
  const now=new Date(), today=iso===localISO(now), nowMin=now.getHours()*60+now.getMinutes(); const out=[];
  for(let s=toMin(w.start);s+duration<=toMin(w.end);s+=duration){
    if(today&&s<=nowMin)continue; const e=s+duration, clash=(x,y)=>s<y&&x<e;
    let status='available';
    if(bookings.some(b=>['ACCEPTED','CONFIRMED'].includes(b.status)&&clash(toMin(b.time),toMin(b.time)+b.duration)))status='booked';
    else if(leaves.some(l=>!l.start||clash(toMin(l.start),toMin(l.end))))status='unavailable';
    else if(bookings.some(b=>b.status==='PENDING_FORM'||b.status==='PENDING_APPROVAL'))status='requested';
    out.push({time:toTime(s),status});
  }
  return out;
}
function resetDemo(){localStorage.removeItem(KEYS.availability);localStorage.removeItem(KEYS.bookings);localStorage.removeItem(KEYS.selected)}
