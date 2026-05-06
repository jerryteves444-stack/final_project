
from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # This displays the names in the list view
    list_display = ('first_name', 'last_name', 'plan_requested', 'amount', 'status', 'created_at')
    search_fields = ('first_name', 'last_name', 'external_id')


