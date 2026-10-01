from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('members/', views.members_view, name='members'),
    path('links/', views.links_view, name='links'),
    path('m/<str:short_code>/', views.redirect_short_link_view, name='redirect_short_link'),
    path('book/', views.landing_page_view, name='landing_page'),
    path('leads/', views.leads_view, name='leads'),
    path('leads/<int:lead_id>/status/', views.update_lead_status_view, name='update_lead_status'),
    path('analytics/', views.analytics_view, name='analytics'),
]
