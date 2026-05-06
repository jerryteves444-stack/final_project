from django.contrib import admin
from .models import Profile, AdminProfile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', "first_name", "last_name", 'middle_name', 'gender', 'user_type', 'address')
    search_fields = ('user__username', 'first_name', 'last_name', 'middle_name', 'address')
    list_filter = ('gender', 'user_type')


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'address', 'created_at')
    search_fields = ('user__username', 'phone')
    list_filter = ('role',)