"""
URL configuration for sales_agent app
"""
from django.urls import path
from sales_agent import views

urlpatterns = [
    # Chat endpoint
    path('chat', views.chat, name='chat'),

    # Admin endpoints
    path('admin/prospects', views.list_prospects, name='list_prospects'),
    path('admin/prospects/<uuid:prospect_id>', views.prospect_detail, name='prospect_detail'),

    # Test endpoints
    path('test/agent/<str:agent_name>', views.test_agent, name='test_agent'),
]
