from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Message


# class CustomUserAdmin(UserAdmin):
#     model = CustomUser
#     list_display = ["username", "email", "is_staff", "is_active"]
#
# admin.site.register(CustomUser, CustomUserAdmin)
#
# # admin.site.register(Message)
#
# @admin.register(Message)
# class MessageAdmin(admin.ModelAdmin):
#     list_display = ("user", "room", "content", "timestamp", "message_deliver", "message_read")
#     search_fields = ("room", "content")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "room", "content", "timestamp", "message_deliver", "message_read")
    list_filter = ("room", "message_deliver", "message_read")
    search_fields = ("content", "user__username", "room")

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "bio", "is_active", "is_staff")
    search_fields = ("username", "email")

