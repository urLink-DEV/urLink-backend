from django.contrib import admin
from django.contrib.auth import get_user_model

from server.models.alarm import Alarm
from server.models.category import Category
from server.models.url import Url

User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    list_display = ('sign_up_type', 'email', 'username', 'is_superuser', 'date_joined')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'updated_at')


class UrlAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'path', 'updated_at')


class AlarmAdmin(admin.ModelAdmin):
    list_display = ('user', 'url', 'has_been_sent', 'has_done', 'has_read', 'reserved_time', 'updated_at')


admin.site.register(User, UserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Url, UrlAdmin)
admin.site.register(Alarm, AlarmAdmin)
