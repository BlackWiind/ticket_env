from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User,Department


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'Custom Field Heading',
            {
                'fields': (
                    'department',
                    'is_customer',
                    'is_engineer',
                )
            }
        )
    )


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    list_display_links = ('id', 'name',)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Department, DepartmentAdmin)
