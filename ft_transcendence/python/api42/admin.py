from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('login', 'first_name', 'is_active')
    search_fields = ('login', 'first_name')
