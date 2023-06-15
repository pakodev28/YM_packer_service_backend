from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Table

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'id', 'created_date']


admin.site.register(Table)
