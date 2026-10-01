import secrets
import string
from datetime import datetime, timedelta
from django.utils import timezone

class MockMember:
    def __init__(self, id, name, email, member_id, created_at, total_visits=0, total_leads=0, qualified_leads=0, total_bookings=0):
        self.id = id
        self.name = name
        self.email = email
        self.member_id = member_id
        if isinstance(created_at, str):
            try:
                self.created_at = datetime.fromisoformat(created_at)
            except ValueError:
                self.created_at = timezone.now()
        else:
            self.created_at = created_at
        self.total_visits = total_visits
        self.total_leads = total_leads
        self.qualified_leads = qualified_leads
        self.total_bookings = total_bookings

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'member_id': self.member_id,
            'created_at': self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else str(self.created_at),
        }


class MockLink:
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('whatsapp', 'WhatsApp'),
        ('linkedin', 'LinkedIn'),
        ('facebook', 'Facebook'),
        ('email', 'Email'),
        ('other', 'Other'),
    ]

    def __init__(self, id, member, platform, campaign, short_code, created_at, visit_count=0, lead_count=0, qualified_count=0, booking_count=0):
        self.id = id
        self.member = member  # MockMember object
        self.platform = platform
        self.campaign = campaign
        self.short_code = short_code
        self.destination_url = '/book/'
        if isinstance(created_at, str):
            try:
                self.created_at = datetime.fromisoformat(created_at)
            except ValueError:
                self.created_at = timezone.now()
        else:
            self.created_at = created_at
        self.visit_count = visit_count
        self.lead_count = lead_count
        self.qualified_count = qualified_count
        self.booking_count = booking_count

    def get_platform_display(self):
        return dict(self.PLATFORM_CHOICES).get(self.platform, self.platform.title())

    def to_dict(self):
        return {
            'id': self.id,
            'member_id': self.member.id if self.member else None,
            'platform': self.platform,
            'campaign': self.campaign,
            'short_code': self.short_code,
            'created_at': self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else str(self.created_at),
            'visit_count': self.visit_count,
        }


class MockLead:
    STATUS_CHOICES = [
        ('new', 'New'),
        ('qualified', 'Qualified'),
        ('booked', 'Booked'),
    ]

    def __init__(self, id, link, name, email, phone, status, created_at):
        self.id = id
        self.link = link  # MockLink object or None
        self.name = name
        self.email = email
        self.phone = phone
        self.status = status
        if isinstance(created_at, str):
            try:
                self.created_at = datetime.fromisoformat(created_at)
            except ValueError:
                self.created_at = timezone.now()
        else:
            self.created_at = created_at
        self.updated_at = self.created_at

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status.title())

    def to_dict(self):
        return {
            'id': self.id,
            'link_id': self.link.id if self.link else None,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'status': self.status,
            'created_at': self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else str(self.created_at),
        }


class MockVisit:
    def __init__(self, id, link, ip_address, user_agent, timestamp):
        self.id = id
        self.link = link  # MockLink object
        self.ip_address = ip_address
        self.user_agent = user_agent
        if isinstance(timestamp, str):
            try:
                self.timestamp = datetime.fromisoformat(timestamp)
            except ValueError:
                self.timestamp = timezone.now()
        else:
            self.timestamp = timestamp

    def to_dict(self):
        return {
            'id': self.id,
            'link_id': self.link.id if self.link else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat() if hasattr(self.timestamp, 'isoformat') else str(self.timestamp),
        }


def get_initial_members():
    now = timezone.now()
    return [
        {'id': 1, 'name': 'Anika Reddy', 'email': 'anika@shriram.com', 'member_id': 'MEM101', 'created_at': (now - timedelta(days=30)).isoformat()},
        {'id': 2, 'name': 'Rahul Sharma', 'email': 'rahul@shriram.com', 'member_id': 'MEM102', 'created_at': (now - timedelta(days=25)).isoformat()},
        {'id': 3, 'name': 'Priya Patel', 'email': 'priya@shriram.com', 'member_id': 'MEM103', 'created_at': (now - timedelta(days=18)).isoformat()},
        {'id': 4, 'name': 'Vikram Malhotra', 'email': 'vikram@shriram.com', 'member_id': 'MEM104', 'created_at': (now - timedelta(days=10)).isoformat()},
    ]


def get_initial_links():
    now = timezone.now()
    return [
        {'id': 1, 'member_id': 1, 'platform': 'instagram', 'campaign': 'september_promo', 'short_code': 'IGSEP9', 'created_at': (now - timedelta(days=20)).isoformat(), 'visit_count': 84},
        {'id': 2, 'member_id': 1, 'platform': 'linkedin', 'campaign': 'b2b_outreach', 'short_code': 'LINKIN', 'created_at': (now - timedelta(days=15)).isoformat(), 'visit_count': 58},
        {'id': 3, 'member_id': 2, 'platform': 'whatsapp', 'campaign': 'direct_connect', 'short_code': 'WACHAT', 'created_at': (now - timedelta(days=22)).isoformat(), 'visit_count': 98},
        {'id': 4, 'member_id': 3, 'platform': 'facebook', 'campaign': 'autumn_festival', 'short_code': 'FBAUTM', 'created_at': (now - timedelta(days=16)).isoformat(), 'visit_count': 115},
        {'id': 5, 'member_id': 4, 'platform': 'email', 'campaign': 'newsletter_q3', 'short_code': 'EMLNEW', 'created_at': (now - timedelta(days=8)).isoformat(), 'visit_count': 76},
    ]


def get_initial_leads():
    now = timezone.now()
    return [
        {'id': 101, 'link_id': 1, 'name': 'Aarav Verma', 'email': 'aarav.v@gmail.com', 'phone': '+91 98765 43210', 'status': 'booked', 'created_at': (now - timedelta(hours=2)).isoformat()},
        {'id': 102, 'link_id': 3, 'name': 'Sneha Kapoor', 'email': 'sneha.k@yahoo.com', 'phone': '+91 98123 45678', 'status': 'qualified', 'created_at': (now - timedelta(hours=5)).isoformat()},
        {'id': 103, 'link_id': 4, 'name': 'Rohan Mehta', 'email': 'rohan.m@outlook.com', 'phone': '+91 97654 32109', 'status': 'new', 'created_at': (now - timedelta(days=1)).isoformat()},
        {'id': 104, 'link_id': 2, 'name': 'Kavya Iyer', 'email': 'kavya.i@techcorp.in', 'phone': '+91 99887 76655', 'status': 'booked', 'created_at': (now - timedelta(days=2)).isoformat()},
        {'id': 105, 'link_id': 5, 'name': 'Amitabh Joshi', 'email': 'ajoshi@enterprise.com', 'phone': '+91 98334 11223', 'status': 'qualified', 'created_at': (now - timedelta(days=3)).isoformat()},
        {'id': 106, 'link_id': 1, 'name': 'Neha Gupta', 'email': 'neha.g@startup.io', 'phone': '+91 91234 56789', 'status': 'new', 'created_at': (now - timedelta(days=4)).isoformat()},
        {'id': 107, 'link_id': None, 'name': 'Suresh Nair', 'email': 'suresh.nair@gmail.com', 'phone': '+91 94455 66778', 'status': 'booked', 'created_at': (now - timedelta(days=5)).isoformat()},
    ]


def get_initial_visits():
    now = timezone.now()
    return [
        {'id': 1, 'link_id': 1, 'ip_address': '192.168.1.1', 'user_agent': 'Mozilla/5.0', 'timestamp': (now - timedelta(minutes=15)).isoformat()},
        {'id': 2, 'link_id': 3, 'ip_address': '192.168.1.2', 'user_agent': 'Mozilla/5.0', 'timestamp': (now - timedelta(hours=1)).isoformat()},
        {'id': 3, 'link_id': 4, 'ip_address': '192.168.1.3', 'user_agent': 'Mozilla/5.0', 'timestamp': (now - timedelta(hours=3)).isoformat()},
        {'id': 4, 'link_id': 2, 'ip_address': '192.168.1.4', 'user_agent': 'Mozilla/5.0', 'timestamp': (now - timedelta(hours=6)).isoformat()},
        {'id': 5, 'link_id': 5, 'ip_address': '192.168.1.5', 'user_agent': 'Mozilla/5.0', 'timestamp': (now - timedelta(hours=12)).isoformat()},
    ]


def get_mock_store(request):
    if 'mock_members' not in request.session:
        request.session['mock_members'] = get_initial_members()
    if 'mock_links' not in request.session:
        request.session['mock_links'] = get_initial_links()
    if 'mock_leads' not in request.session:
        request.session['mock_leads'] = get_initial_leads()
    if 'mock_visits' not in request.session:
        request.session['mock_visits'] = get_initial_visits()

    m_data = request.session['mock_members']
    l_data = request.session['mock_links']
    ld_data = request.session['mock_leads']
    v_data = request.session['mock_visits']

    # 1. Hydrate Members
    members = []
    members_map = {}
    for d in m_data:
        m = MockMember(
            id=d['id'],
            name=d['name'],
            email=d['email'],
            member_id=d['member_id'],
            created_at=d['created_at']
        )
        members.append(m)
        members_map[m.id] = m

    # 2. Hydrate Links
    links = []
    links_map = {}
    for d in l_data:
        member_obj = members_map.get(d['member_id'])
        lk = MockLink(
            id=d['id'],
            member=member_obj,
            platform=d['platform'],
            campaign=d['campaign'],
            short_code=d['short_code'],
            created_at=d['created_at'],
            visit_count=d.get('visit_count', 0)
        )
        links.append(lk)
        links_map[lk.id] = lk

    # 3. Hydrate Leads
    leads = []
    for d in ld_data:
        link_obj = links_map.get(d['link_id'])
        ld = MockLead(
            id=d['id'],
            link=link_obj,
            name=d['name'],
            email=d['email'],
            phone=d['phone'],
            status=d['status'],
            created_at=d['created_at']
        )
        leads.append(ld)

    # 4. Hydrate Visits
    visits = []
    for d in v_data:
        link_obj = links_map.get(d['link_id'])
        vt = MockVisit(
            id=d['id'],
            link=link_obj,
            ip_address=d.get('ip_address', ''),
            user_agent=d.get('user_agent', ''),
            timestamp=d['timestamp']
        )
        visits.append(vt)

    # Aggregations on links
    for lk in links:
        lk_leads = [ld for ld in leads if ld.link and ld.link.id == lk.id]
        lk.lead_count = len(lk_leads)
        lk.qualified_count = sum(1 for ld in lk_leads if ld.status == 'qualified')
        lk.booking_count = sum(1 for ld in lk_leads if ld.status == 'booked')

    # Aggregations on members
    for m in members:
        m_links = [lk for lk in links if lk.member and lk.member.id == m.id]
        m_link_ids = {lk.id for lk in m_links}
        m.total_visits = sum(lk.visit_count for lk in m_links)
        m.total_leads = sum(1 for ld in leads if ld.link and ld.link.id in m_link_ids)
        m.qualified_leads = sum(1 for ld in leads if ld.link and ld.link.id in m_link_ids and ld.status == 'qualified')
        m.total_bookings = sum(1 for ld in leads if ld.link and ld.link.id in m_link_ids and ld.status == 'booked')

    return members, links, leads, visits


def add_mock_member(request, name, email, member_id):
    members_data = request.session.get('mock_members', get_initial_members())
    next_id = max((m['id'] for m in members_data), default=0) + 1
    new_m = {
        'id': next_id,
        'name': name,
        'email': email,
        'member_id': member_id,
        'created_at': timezone.now().isoformat()
    }
    members_data.append(new_m)
    request.session['mock_members'] = members_data
    request.session.modified = True
    return new_m


def add_mock_link(request, member_id, platform, campaign, short_code):
    links_data = request.session.get('mock_links', get_initial_links())
    next_id = max((l['id'] for l in links_data), default=0) + 1
    new_l = {
        'id': next_id,
        'member_id': int(member_id),
        'platform': platform,
        'campaign': campaign,
        'short_code': short_code,
        'created_at': timezone.now().isoformat(),
        'visit_count': 0
    }
    links_data.append(new_l)
    request.session['mock_links'] = links_data
    request.session.modified = True
    return new_l


def add_mock_lead(request, link_id, name, email, phone):
    leads_data = request.session.get('mock_leads', get_initial_leads())
    next_id = max((ld['id'] for ld in leads_data), default=100) + 1
    new_ld = {
        'id': next_id,
        'link_id': int(link_id) if link_id else None,
        'name': name,
        'email': email,
        'phone': phone,
        'status': 'new',
        'created_at': timezone.now().isoformat()
    }
    leads_data.append(new_ld)
    request.session['mock_leads'] = leads_data
    request.session.modified = True

    members, links, leads, visits = get_mock_store(request)
    created_lead_obj = next((ld for ld in leads if ld.id == next_id), None)
    return created_lead_obj


def update_mock_lead_status(request, lead_id, new_status):
    leads_data = request.session.get('mock_leads', get_initial_leads())
    for ld in leads_data:
        if str(ld['id']) == str(lead_id):
            ld['status'] = new_status
            break
    request.session['mock_leads'] = leads_data
    request.session.modified = True

    members, links, leads, visits = get_mock_store(request)
    updated_lead_obj = next((ld for ld in leads if str(ld.id) == str(lead_id)), None)
    return updated_lead_obj


def increment_mock_visit(request, link_id):
    links_data = request.session.get('mock_links', get_initial_links())
    for l in links_data:
        if str(l['id']) == str(link_id):
            l['visit_count'] = l.get('visit_count', 0) + 1
            break
    request.session['mock_links'] = links_data

    visits_data = request.session.get('mock_visits', get_initial_visits())
    next_id = max((v['id'] for v in visits_data), default=0) + 1
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR', '127.0.0.1')
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    visits_data.append({
        'id': next_id,
        'link_id': int(link_id),
        'ip_address': ip,
        'user_agent': user_agent,
        'timestamp': timezone.now().isoformat()
    })
    request.session['mock_visits'] = visits_data
    request.session.modified = True


def generate_mock_short_code(links):
    chars = string.ascii_uppercase + string.digits
    existing_codes = {l.short_code.upper() for l in links}
    while True:
        code = ''.join(secrets.choice(chars) for _ in range(6))
        if code not in existing_codes:
            return code
