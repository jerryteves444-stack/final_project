from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('upgrade/', views.payment_page, name='payments'),
    path('process/', views.process_payment, name='checkout'),
    path('success/', views.success, name='success'),
    path('failure/', views.failure, name='failure'),
    # Simplified these names to match your register.html tags
    path('solo/', views.solo_registration, name='solo'),
    path('family/', views.family_registration, name='family'),
    path('solo_pay/', views.solo_payment, name='solo_pay'),
    path('family_pay/', views.family_payment, name='family_pay'),
    path('mortuary/', views.mortuary_registration, name='mortuary'),
    path('donation/', views.donation_page, name='donation'),
    path('process-mortuary/', views.process_mortuary_payment, name='process_mortuary_payment'),
    path('xendit-webhook/', views.xendit_webhook, name='xendit_webhook'),

]