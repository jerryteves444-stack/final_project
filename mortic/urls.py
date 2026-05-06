from django.contrib import admin
from django.urls import path, include
from accounts import views as account_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
                  path('admin/', admin.site.urls),

                  # 🏠 LANDING / LOGIN
                  path('', account_views.login_view, name='login'),

                  # 🔐 AUTH ROUTES
                  path('logout/', account_views.logout_view, name='logout'),
                  path('register/', account_views.register_view, name='register'),

                  # 📁 APP INCLUDES (Namespace usage happens here)
                  path('accounts/', include('accounts.urls')),
                  path('payments/', include('payments.urls')),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 🛠 DEBUG MEDIA SETTINGS
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 🔑 PASSWORD RESET SYSTEM
urlpatterns += [
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html'
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]