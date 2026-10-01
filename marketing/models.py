import secrets
import string
from django.db import models

class MarketingMember(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    member_id = models.CharField(max_length=30, unique=True, help_text="Unique Member ID e.g., MEM101")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.member_id})"

    @property
    def total_visits(self):
        return Visit.objects.filter(link__member=self).count()

    @property
    def total_leads(self):
        return Lead.objects.filter(link__member=self).count()

    @property
    def qualified_leads(self):
        return Lead.objects.filter(link__member=self, status='qualified').count()

    @property
    def total_bookings(self):
        return Lead.objects.filter(link__member=self, status='booked').count()


class MarketingLink(models.Model):
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('whatsapp', 'WhatsApp'),
        ('linkedin', 'LinkedIn'),
        ('facebook', 'Facebook'),
        ('email', 'Email'),
        ('other', 'Other'),
    ]

    member = models.ForeignKey(MarketingMember, on_delete=models.CASCADE, related_name='links')
    platform = models.CharField(max_length=30, choices=PLATFORM_CHOICES, default='instagram')
    campaign = models.CharField(max_length=100, help_text="Campaign name e.g. september_promo")
    short_code = models.CharField(max_length=20, unique=True)
    destination_url = models.CharField(max_length=255, default='/book/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.member.name} - {self.platform} ({self.campaign}) [{self.short_code}]"

    @classmethod
    def generate_short_code(cls):
        chars = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(secrets.choice(chars) for _ in range(6))
            if not cls.objects.filter(short_code=code).exists():
                return code

    @property
    def visit_count(self):
        return self.visits.count()

    @property
    def lead_count(self):
        return self.leads.count()

    @property
    def qualified_count(self):
        return self.leads.filter(status='qualified').count()

    @property
    def booking_count(self):
        return self.leads.filter(status='booked').count()


class Visit(models.Model):
    link = models.ForeignKey(MarketingLink, on_delete=models.CASCADE, related_name='visits')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Visit to {self.link.short_code} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class Lead(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('qualified', 'Qualified'),
        ('booked', 'Booked'),
    ]

    link = models.ForeignKey(MarketingLink, on_delete=models.SET_NULL, null=True, blank=True, related_name='leads')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Lead: {self.name} ({self.get_status_display()})"
