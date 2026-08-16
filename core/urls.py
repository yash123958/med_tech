from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),

    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('donate/', views.add_donation, name='add_donation'),

    path('ngo/', views.ngo_dashboard, name='ngo_dashboard'),
    path('request/<int:id>/', views.request_medicine, name='request_medicine'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve/<int:id>/', views.approve_request),
    path('reject/<int:id>/', views.reject_request),
    path('track/<int:id>/', views.track_request, name='track_request'), 
    path('packed/<int:id>/', views.mark_packed, name='mark_packed'),
    path('out/<int:id>/', views.mark_out_for_delivery, name='mark_out'),
    path('delivered/<int:id>/', views.mark_delivered, name='mark_delivered'),
    path('approve-donation/<int:id>/', views.approve_donation, name='approve_donation'),
    path('reject-donation/<int:id>/', views.reject_donation, name='reject_donation'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)