from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings  # settings se user model import hoga


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)   # email ko unique kar diya

    # optional extra fields
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username


class Message(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.CharField(max_length=100)  # room ka naam
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    message_deliver = models.BooleanField(default=False, blank=True)
    message_read = models.BooleanField(default=False, blank=True)
    is_deleted = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}"
