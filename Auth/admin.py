from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from Auth.models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Specify the fields to display in the admin list view
    list_display = ('username', 'email', 'role', 'nni', 'image', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')

    # Add the custom fields to the admin form
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'image')}),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Custom Fields', {'fields': ('role',)}),  # Include the 'role' field here
    )

    # Add fields for the user creation form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'nni', 'image'),
        }),
    )

    # Fields to include in the admin add/edit view
    search_fields = ('username', 'email', 'role', 'nni')
    ordering = ('username',)

# Register the custom user admin
admin.site.register(CustomUser, CustomUserAdmin)