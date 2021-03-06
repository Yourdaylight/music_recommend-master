from django.contrib import admin

from .models import *


# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "password", "name", "address", "email")
    search_fields = ("username", "name", "address", "phone", "email")


class MusicAdmin(admin.ModelAdmin):
    list_display = ("name", "artist", "album", "artist", 'years','num', 'pic')
    search_fields = ("name", "artist")
    list_filter = ("artist", "album")


class ActionAdmin(admin.ModelAdmin):
    def show_all_join(self, obj):
        return [a.name for a in obj.user.all()]

    def num(self, obj):
        return obj.user.count()

    list_display = ("title", "num", "status")
    search_fields = ("title", "content", "user")
    list_filter = ("status",)


class CommenAdmin(admin.ModelAdmin):
    list_display = ("user", "music", "good", "create_time")
    search_fields = ("user", "music", "good")
    list_filter = ("user", "music")


class LiuyanAdmin(admin.ModelAdmin):
    list_display = ("user", "create_time")
    search_fields = ("user",)
    list_filter = ("user",)


admin.site.register(Tags)
admin.site.register(User, UserAdmin)
admin.site.register(Music, MusicAdmin)


