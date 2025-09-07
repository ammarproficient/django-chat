from django.contrib import admin
from .models import CustomUser, Message, Friendship


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "room", "content", "timestamp", "message_deliver", "message_read")
    list_filter = ("room", "message_deliver", "message_read")
    search_fields = ("content", "user__username", "room")

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "bio", "is_active", "is_staff")
    search_fields = ("username", "email")

admin.site.register(Friendship)
