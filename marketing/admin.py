from django.contrib import admin
from .models import MarketingMember, MarketingLink, Visit, Lead

@admin.register(MarketingMember)
class MarketingMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'member_id', 'created_at')
    search_fields = ('name', 'email', 'member_id')

@admin.register(MarketingLink)
class MarketingLinkAdmin(admin.ModelAdmin):
    list_display = ('short_code', 'member', 'platform', 'campaign', 'created_at')
    list_filter = ('platform', 'member')
    search_fields = ('short_code', 'campaign', 'member__name')

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('link', 'timestamp', 'ip_address')
    list_filter = ('timestamp', 'link__platform')

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'status', 'link', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'phone')
