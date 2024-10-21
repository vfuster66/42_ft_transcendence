
#users/admin.py

#########################################################################################################

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile

#########################################################################################################

@admin.action(description='Activer 2FA pour les comptes sélectionnés')
def activate_2fa(modeladmin, request, queryset):
	for profile in queryset:
		profile.two_factor_enabled = True
		profile.save()
	modeladmin.message_user(request, "2FA activé pour les comptes sélectionnés.")

@admin.action(description='Désactiver 2FA pour les comptes sélectionnés')
def deactivate_2fa(modeladmin, request, queryset):
	for profile in queryset:
		profile.two_factor_enabled = False
		profile.save()
	modeladmin.message_user(request, "2FA désactivé pour les comptes sélectionnés.")

@admin.action(description='Réactiver les comptes sélectionnés')
def reactivate_accounts(modeladmin, request, queryset):
	queryset.update(is_active=True)
	modeladmin.message_user(request, "Comptes sélectionnés réactivés.")

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ['user', 'is_active', 'two_factor_status']
	actions = [activate_2fa, deactivate_2fa, reactivate_accounts]

	def two_factor_status(self, obj):
		return "Activé" if obj.two_factor_enabled else "Désactivé"
	two_factor_status.short_description = "Statut 2FA"

class UserAdmin(BaseUserAdmin):
	list_display = ('username', 'email', 'first_name', 'last_name', 'is_active')
	list_filter = ('is_active',)
	fieldsets = (
		(None, {'fields': ('username', 'password')}),
		('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
		('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
		('Important dates', {'fields': ('last_login', 'date_joined')}),
	)

#########################################################################################################

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

#########################################################################################################

