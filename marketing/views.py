from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from .models import MarketingMember, MarketingLink, Visit, Lead

def dashboard_view(request):
    """
    Main Marketing Dashboard displaying core metrics, funnel, charts, and activity log.
    """
    total_visits = Visit.objects.count()
    total_leads = Lead.objects.count()
    qualified_leads = Lead.objects.filter(status='qualified').count()
    total_appointments = Lead.objects.filter(status='booked').count()

    # Calculate conversion rates
    visit_to_lead_rate = round((total_leads / total_visits * 100), 1) if total_visits > 0 else 0
    lead_to_booked_rate = round((total_appointments / total_leads * 100), 1) if total_leads > 0 else 0

    # Recent activity stream (Visits and Leads combined or recent leads)
    recent_leads = Lead.objects.select_related('link', 'link__member').order_by('-created_at')[:5]
    recent_visits = Visit.objects.select_related('link', 'link__member').order_by('-timestamp')[:5]

    # Source / Platform performance data for Chart.js
    platforms = [choice[0] for choice in MarketingLink.PLATFORM_CHOICES]
    platform_labels = [choice[1] for choice in MarketingLink.PLATFORM_CHOICES]
    
    platform_visits = []
    platform_leads = []
    platform_bookings = []

    for code, label in MarketingLink.PLATFORM_CHOICES:
        v_cnt = Visit.objects.filter(link__platform=code).count()
        l_cnt = Lead.objects.filter(link__platform=code).count()
        b_cnt = Lead.objects.filter(link__platform=code, status='booked').count()
        platform_visits.append(v_cnt)
        platform_leads.append(l_cnt)
        platform_bookings.append(b_cnt)

    # Member performance data for Chart.js
    members = MarketingMember.objects.all()[:10]
    member_names = [m.name for m in members]
    member_visits = [m.total_visits for m in members]
    member_leads = [m.total_leads for m in members]
    member_bookings = [m.total_bookings for m in members]

    # Funnel stages summary
    funnel = {
        'total_links': MarketingLink.objects.count(),
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
    List marketing members and handle member creation.
    """
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        member_id = request.POST.get('member_id', '').strip()

        if not name or not email:
            messages.error(request, "Name and Email are required fields.")
        elif MarketingMember.objects.filter(email=email).exists():
            messages.error(request, f"A member with email '{email}' already exists.")
        else:
            if not member_id:
                # Auto generate member id
                count = MarketingMember.objects.count() + 101
                member_id = f"MEM{count}"
                while MarketingMember.objects.filter(member_id=member_id).exists():
                    count += 1
                    member_id = f"MEM{count}"

            if MarketingMember.objects.filter(member_id=member_id).exists():
                messages.error(request, f"Member ID '{member_id}' is already taken.")
            else:
                MarketingMember.objects.create(name=name, email=email, member_id=member_id)
                messages.success(request, f"Marketing member '{name}' ({member_id}) added successfully!")
                return redirect('members')

    members_list = MarketingMember.objects.all()
    context = {
        'members': members_list,
    }
    return render(request, 'marketing/members.html', context)


def links_view(request):
    """
    List all marketing tracking links and handle creation of new links.
    """
    if request.method == 'POST':
        member_id = request.POST.get('member')
        platform = request.POST.get('platform')
        campaign = request.POST.get('campaign', '').strip() or 'general'

        member = get_object_or_404(MarketingMember, id=member_id)
        short_code = MarketingLink.generate_short_code()

        link = MarketingLink.objects.create(
            member=member,
            platform=platform,
            campaign=campaign,
            short_code=short_code,
            destination_url='/book/'
        )
        messages.success(request, f"Trackable Link created! Short Code: /m/{short_code}")
        return redirect('links')

    links_list = MarketingLink.objects.select_related('member').all()
    members_list = MarketingMember.objects.all()
    platform_choices = MarketingLink.PLATFORM_CHOICES

    context = {
        'links': links_list,
        'members': members_list,
        'platform_choices': platform_choices,
    }
    return render(request, 'marketing/links.html', context)


def redirect_short_link_view(request, short_code):
    """
    Handles /m/<short_code>/ short marketing links:
    - Increments visit count by logging Visit object
    - Stores attribution in session
    - Redirects to common booking page with query parameters
    """
    link = get_object_or_404(MarketingLink, short_code=short_code)

    # Extract client IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    user_agent = request.META.get('HTTP_USER_AGENT', '')

    # Record Visit
    Visit.objects.create(
        link=link,
        ip_address=ip,
        user_agent=user_agent
    )

    # Store attribution in session
    request.session['marketing_link_id'] = link.id
    request.session['marketing_short_code'] = link.short_code

    # Build target redirect URL with explicit query parameters
    target_url = f"/book/?short_code={link.short_code}&member={link.member.member_id}&source={link.platform}&campaign={link.campaign}"
    return redirect(target_url)


def landing_page_view(request):
    """
    Landing / Booking page (/book/):
    - Shows demo booking form
    - Checks URL query parameters or session for attribution
    - Processes Lead creation linked to MarketingLink
    """
    short_code = request.GET.get('short_code')
    member_code = request.GET.get('member')
    source = request.GET.get('source')
    campaign = request.GET.get('campaign')

    link = None

    # Try matching by short code
    if short_code:
        link = MarketingLink.objects.filter(short_code=short_code).first()

    # Try matching by member ID, source, campaign
    if not link and member_code and source and campaign:
        link = MarketingLink.objects.filter(
            member__member_id=member_code,
            platform=source,
            campaign=campaign
        ).first()

    # Fallback to session
    if not link and 'marketing_link_id' in request.session:
        link = MarketingLink.objects.filter(id=request.session['marketing_link_id']).first()

    # If direct landing without short link redirect, but query parameters exist, record visit
    if (short_code or (member_code and source and campaign)) and link:
        # Save to session
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
            new_lead = Lead.objects.create(
                link=link,
                name=name,
                email=email,
                phone=phone,
                status='new'
            )
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

    leads_qs = Lead.objects.select_related('link', 'link__member').all()

    if status_filter in ['new', 'qualified', 'booked']:
        leads_qs = leads_qs.filter(status=status_filter)

    if search_query:
        leads_qs = leads_qs.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(link__member__name__icontains=search_query)
        )

    status_choices = Lead.STATUS_CHOICES

    context = {
        'leads': leads_qs,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': status_choices,
    }
    return render(request, 'marketing/leads.html', context)


def update_lead_status_view(request, lead_id):
    """
    Update lead status (New, Qualified, Booked) via POST request.
    """
    lead = get_object_or_404(Lead, id=lead_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Lead.STATUS_CHOICES):
            old_status_display = lead.get_status_display()
            lead.status = new_status
            lead.save()
            messages.success(request, f"Lead '{lead.name}' status updated from {old_status_display} to {lead.get_status_display()}.")

    next_url = request.META.get('HTTP_REFERER', 'leads')
    return redirect(next_url)


def analytics_view(request):
    """
    Detailed analytics breakdown page by:
    - Marketing Member
    - Platform / Source
    - Campaign
    - Individual Link
    """
    # 1. Member Breakdown
    members = MarketingMember.objects.all()
    member_analytics = []
    for m in members:
        visits = m.total_visits
        leads = m.total_leads
        qualified = m.qualified_leads
        bookings = m.total_bookings
        conv_rate = round((bookings / visits * 100), 1) if visits > 0 else 0
        member_analytics.append({
            'member': m,
            'visits': visits,
            'leads': leads,
            'qualified': qualified,
            'bookings': bookings,
            'conversion_rate': conv_rate,
        })

    # 2. Platform Breakdown
    platform_analytics = []
    for code, label in MarketingLink.PLATFORM_CHOICES:
        visits = Visit.objects.filter(link__platform=code).count()
        leads = Lead.objects.filter(link__platform=code).count()
        qualified = Lead.objects.filter(link__platform=code, status='qualified').count()
        bookings = Lead.objects.filter(link__platform=code, status='booked').count()
        conv_rate = round((bookings / visits * 100), 1) if visits > 0 else 0
        platform_analytics.append({
            'code': code,
            'platform': label,
            'visits': visits,
            'leads': leads,
            'qualified': qualified,
            'bookings': bookings,
            'conversion_rate': conv_rate,
        })

    # 3. Campaign Breakdown
    campaigns = MarketingLink.objects.values_list('campaign', flat=True).distinct()
    campaign_analytics = []
    for c in campaigns:
        visits = Visit.objects.filter(link__campaign=c).count()
        leads = Lead.objects.filter(link__campaign=c).count()
        qualified = Lead.objects.filter(link__campaign=c, status='qualified').count()
        bookings = Lead.objects.filter(link__campaign=c, status='booked').count()
        conv_rate = round((bookings / visits * 100), 1) if visits > 0 else 0
        campaign_analytics.append({
            'campaign': c,
            'visits': visits,
            'leads': leads,
            'qualified': qualified,
            'bookings': bookings,
            'conversion_rate': conv_rate,
        })

    # 4. Link Breakdown
    links = MarketingLink.objects.select_related('member').all()

    context = {
        'member_analytics': member_analytics,
        'platform_analytics': platform_analytics,
        'campaign_analytics': campaign_analytics,
        'links': links,
    }
    return render(request, 'marketing/analytics.html', context)
