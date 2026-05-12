from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    USER_TYPES = (
        ('student', 'Student'),
        ('tutor', 'Tutor/Author'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
        
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='student')



class UserActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'date')



class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account_notifications"   # ✅ FIX
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)



    