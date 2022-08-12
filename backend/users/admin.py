from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Subscribe


@admin.register(User)
class UserAdmin(UserAdmin):
    list_filter = ('email', 'first_name')


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
