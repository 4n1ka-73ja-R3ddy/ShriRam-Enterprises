from django.shortcuts import render, redirect
from django.contrib import messages
from .mock_data import (
    MockMember,
    MockLink,
    MockLead,
    MockVisit,
    get_mock_store,
    add_mock_member,
    add_mock_link,
    add_mock_lead,
    update_mock_lead_status,
    increment_mock_visit,
    generate_mock_short_code,
)

def dashboard_view(request):
    """
    Main Marketing Dashboard displaying core metrics, funnel, charts, and activity log.
    Powered by in-memory / session mock data (no DB queries required).
    """
    members, links, leads, visits = get_mock_store(request)

    total_visits = sum(l.visit_count for l in links)
    total_leads = len(leads)
    qualified_leads = sum(1 for l in leads if l.status == 'qualified')
    total_appointments = sum(1 for l in leads if l.status == 'booked')

    visit_to_lead_rate = round((total_leads / total_visits * 100), 1) if total_visits > 0 else 0
    lead_to_booked_rate = round((total_appointments / total_leads * 100), 1) if total_leads > 0 else 0

    recent_leads = sorted(leads, key=lambda x: x.created_at, reverse=True)[:5]
    recent_visits = sorted(visits, key=lambda x: x.timestamp, reverse=True)[:5]

    platform_choices = MockLink.PLATFORM_CHOICES
    platform_labels = [label for code, label in platform_choices]

    platform_visits = []
    platform_leads = []
    platform_bookings = []

    for code, label in platform_choices:
        p_links = [l for l in links if l.platform == code]
        v_cnt = sum(l.visit_count for l in p_links)
        p_link_ids = {l.id for l in p_links}
        l_cnt = sum(1 for ld in leads if ld.link and ld.link.id in p_link_ids)
        b_cnt = sum(1 for ld in leads if ld.link and ld.link.id in p_link_ids and ld.status == 'booked')
        platform_visits.append(v_cnt)
        platform_leads.append(l_cnt)
        platform_bookings.append(b_cnt)

    member_names = [m.name for m in members[:10]]
    member_visits = [m.total_visits for m in members[:10]]
    member_leads = [m.total_leads for m in members[:10]]
    member_bookings = [m.total_bookings for m in members[:10]]

    funnel = {
        'total_links': len(links),
        'visits': total_visits,
        'leads': total_leads,
        'qualified': qualified_leads,
        'booked': total_appointments,
    }

    context = {
        'total_visits': total_visits,
        'total_leads': total_leads,
        'qualified_leads': qualified_leads,
        'total_appointments': total_appointments,
        'visit_to_lead_rate': visit_to_lead_rate,
        'lead_to_booked_rate': lead_to_booked_rate,
        'recent_leads': recent_leads,
        'recent_visits': recent_visits,
        'platform_labels': platform_labels,
        'platform_visits': platform_visits,
        'platform_leads': platform_leads,
        'platform_bookings': platform_bookings,
        'member_names': member_names,
        'member_visits': member_visits,
        'member_leads': member_leads,
        'member_bookings': member_bookings,
        'funnel': funnel,
    }
    return render(request, 'marketing/dashboard.html', context)


def members_view(request):
    """
    List marketing members and handle member creation in session mock store.
    """
    members, links, leads, visits = get_mock_store(request)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        member_id = request.POST.get('member_id', '').strip()

        if not name or not email:
            messages.error(request, "Name and Email are required fields.")
        elif any(m.email.lower() == email.lower() for m in members):
            messages.error(request, f"A member with email '{email}' already exists.")
        else:
            if not member_id:
                count = len(members) + 101
                member_id = f"MEM{count}"
                while any(m.member_id == member_id for m in members):
                    count += 1
                    member_id = f"MEM{count}"

            if any(m.member_id == member_id for m in members):
                messages.error(request, f"Member ID '{member_id}' is already taken.")
            else:
                add_mock_member(request, name, email, member_id)
                messages.success(request, f"Marketing member '{name}' ({member_id}) added successfully!")
                return redirect('members')

    members, _, _, _ = get_mock_store(request)
    context = {
        'members': members,
    }
    return render(request, 'marketing/members.html', context)


def links_view(request):
    """
    List all marketing tracking links and handle creation of new links.
    """
    members, links, leads, visits = get_mock_store(request)

    if request.method == 'POST':
        member_id = request.POST.get('member')
        platform = request.POST.get('platform')
        campaign = request.POST.get('campaign', '').strip() or 'general'

        member_obj = next((m for m in members if str(m.id) == str(member_id)), None)
        if member_obj:
            short_code = generate_mock_short_code(links)
            add_mock_link(request, member_obj.id, platform, campaign, short_code)
            messages.success(request, f"Trackable Link created! Short Code: /m/{short_code}")
            return redirect('links')
        else:
            messages.error(request, "Selected member not found.")

    members, links, _, _ = get_mock_store(request)
    platform_choices = MockLink.PLATFORM_CHOICES

    context = {
        'links': links,
        'members': members,
        'platform_choices': platform_choices,
    }
    return render(request, 'marketing/links.html', context)


def redirect_short_link_view(request, short_code):
    """
    Handles /m/<short_code>/ short marketing links without database operations.
    """
    members, links, leads, visits = get_mock_store(request)

    link = next((l for l in links if l.short_code.lower() == short_code.lower()), None)
    if not link:
        link = links[0] if links else None

    if link:
        increment_mock_visit(request, link.id)
        request.session['marketing_link_id'] = link.id
        request.session['marketing_short_code'] = link.short_code
        target_url = f"/book/?short_code={link.short_code}&member={link.member.member_id}&source={link.platform}&campaign={link.campaign}"
    else:
        target_url = "/book/"

    return redirect(target_url)


def landing_page_view(request):
    """
    Landing / Booking page (/book/):
    Shows demo booking form, checks referral attribution, and processes lead submissions without DB.
    """
    short_code = request.GET.get('short_code')
    member_code = request.GET.get('member')
    source = request.GET.get('source')
    campaign = request.GET.get('campaign')

    members, links, leads, visits = get_mock_store(request)

    link = None

    if short_code:
        link = next((l for l in links if l.short_code.lower() == short_code.lower()), None)

    if not link and member_code and source and campaign:
        link = next((l for l in links if l.member and l.member.member_id.lower() == member_code.lower() and l.platform == source and l.campaign == campaign), None)

    if not link and 'marketing_link_id' in request.session:
        link_id = request.session['marketing_link_id']
        link = next((l for l in links if l.id == link_id), None)

    if (short_code or (member_code and source and campaign)) and link:
        request.session['marketing_link_id'] = link.id

    submitted = False
    new_lead = None

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()

        if not name or not email or not phone:
            messages.error(request, "Please fill in all fields (Name, Email, Phone).")
        else:
            link_id = link.id if link else None
            new_lead = add_mock_lead(request, link_id, name, email, phone)
            submitted = True
            messages.success(request, "Thank you! Your appointment request has been submitted.")

    context = {
        'attribution_link': link,
        'submitted': submitted,
        'new_lead': new_lead,
        'member_code': member_code or (link.member.member_id if link else None),
        'source': source or (link.platform if link else None),
        'campaign': campaign or (link.campaign if link else None),
    }
    return render(request, 'marketing/landing_page.html', context)


def leads_view(request):
    """
    Lists leads with filtering options and status toggles.
    """
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('q', '').strip()

    members, links, leads, visits = get_mock_store(request)

    filtered_leads = leads

    if status_filter in ['new', 'qualified', 'booked']:
        filtered_leads = [l for l in filtered_leads if l.status == status_filter]

    if search_query:
        q = search_query.lower()
        filtered_leads = [
            l for l in filtered_leads
            if q in l.name.lower()
            or q in l.email.lower()
            or q in l.phone.lower()
            or (l.link and l.link.member and q in l.link.member.name.lower())
        ]

    status_choices = MockLead.STATUS_CHOICES

    context = {
        'leads': filtered_leads,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': status_choices,
    }
    return render(request, 'marketing/leads.html', context)


def update_lead_status_view(request, lead_id):
    """
    Update lead status (New, Qualified, Booked) via POST request.
    """
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(MockLead.STATUS_CHOICES):
            lead = update_mock_lead_status(request, lead_id, new_status)
            if lead:
                messages.success(request, f"Lead '{lead.name}' status updated to {lead.get_status_display()}.")

    next_url = request.META.get('HTTP_REFERER', '/leads/')
    return redirect(next_url)


def analytics_view(request):
    """
    Detailed analytics breakdown page by Member, Platform, Campaign, and Link.
    """
    members, links, leads, visits = get_mock_store(request)

    # 1. Member Breakdown
    member_analytics = []
    for m in members:
        v = m.total_visits
        l = m.total_leads
        q = m.qualified_leads
        b = m.total_bookings
        conv_rate = round((b / v * 100), 1) if v > 0 else 0
        member_analytics.append({
            'member': m,
            'visits': v,
            'leads': l,
            'qualified': q,
            'bookings': b,
            'conversion_rate': conv_rate,
        })

    # 2. Platform Breakdown
    platform_analytics = []
    for code, label in MockLink.PLATFORM_CHOICES:
        p_links = [lk for lk in links if lk.platform == code]
        p_link_ids = {lk.id for lk in p_links}
        v = sum(lk.visit_count for lk in p_links)
        l = sum(1 for ld in leads if ld.link and ld.link.id in p_link_ids)
        q = sum(1 for ld in leads if ld.link and ld.link.id in p_link_ids and ld.status == 'qualified')
        b = sum(1 for ld in leads if ld.link and ld.link.id in p_link_ids and ld.status == 'booked')
        conv_rate = round((b / v * 100), 1) if v > 0 else 0
        platform_analytics.append({
            'code': code,
            'platform': label,
            'visits': v,
            'leads': l,
            'qualified': q,
            'bookings': b,
            'conversion_rate': conv_rate,
        })

    # 3. Campaign Breakdown
    campaigns = list(dict.fromkeys(lk.campaign for lk in links if lk.campaign))
    campaign_analytics = []
    for c in campaigns:
        c_links = [lk for lk in links if lk.campaign == c]
        c_link_ids = {lk.id for lk in c_links}
        v = sum(lk.visit_count for lk in c_links)
        l = sum(1 for ld in leads if ld.link and ld.link.id in c_link_ids)
        q = sum(1 for ld in leads if ld.link and ld.link.id in c_link_ids and ld.status == 'qualified')
        b = sum(1 for ld in leads if ld.link and ld.link.id in c_link_ids and ld.status == 'booked')
        conv_rate = round((b / v * 100), 1) if v > 0 else 0
        campaign_analytics.append({
            'campaign': c,
            'visits': v,
            'leads': l,
            'qualified': q,
            'bookings': b,
            'conversion_rate': conv_rate,
        })

    context = {
        'member_analytics': member_analytics,
        'platform_analytics': platform_analytics,
        'campaign_analytics': campaign_analytics,
        'links': links,
    }
    return render(request, 'marketing/analytics.html', context)
