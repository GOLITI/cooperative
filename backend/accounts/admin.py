from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
	ordering = ('email',)
	list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff')
	list_filter = ('is_active', 'is_staff', 'is_superuser')
	search_fields = ('email', 'first_name', 'last_name')

	fieldsets = (
		(None, {'fields': ('email', 'password')}),
		(_('Informations personnelles'), {'fields': ('first_name', 'last_name', 'phone_number', 'organisation', 'title')}),
		(_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
		(_('Dates importantes'), {'fields': ('last_login', 'date_joined')}),
	)

	add_fieldsets = (
		(
			None,
			{
				'classes': ('wide',),
				'fields': ('email', 'password1', 'password2', 'is_staff', 'is_superuser'),
			},
		),
	)
