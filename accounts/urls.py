from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ==========================
    # 🔐 AUTHENTICATION
    # ==========================
    # Kini ang default page (Login) inig abli sa site
    path('', views.login_view, name='login_root'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # ==========================
    # 🏠 CORE FEATURES (FEED & PROFILE)
    # ==========================
    path('home/', views.home, name='home'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/<int:pk>/', views.view_profile, name='view_profile'),
    path('members/', views.all_members, name='all_members_page'),
    path('members/search/', views.member_list_view, name='member_search'),
    path('members/', views.all_members, name='all_members'),

    # ==========================
    # 📝 POST & COMMENT ACTIONS
    # ==========================
    path('post/edit/<int:post_id>/', views.edit_post, name='edit_post'),
    path('post/delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('comment/edit/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),

    # ==========================
    # 🛠️ ADMIN & USER MANAGEMENT
    # ==========================
    path('admin-dashboard/', views.admin_page, name='admin_page'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/update/<int:id>/', views.update_user, name='update_user'),
    path('users/delete/<int:id>/', views.delete_user, name='delete_user'),
]

# Para mugana ang mga uploaded pictures (Profile & Cover)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)