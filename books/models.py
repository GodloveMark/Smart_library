
from django.db import models
from django.urls import reverse
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Book(models.Model):
    tutor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    file = models.FileField(upload_to='books/')  # ✅ PDF upload
    cover = models.ImageField(upload_to='covers/', blank=True, null=True)

    price = models.FloatField(null=True, blank=True)
    book_available = models.BooleanField(default=True)
    is_indexed = models.BooleanField(default=False)

    #created_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class Order(models.Model):
	product = models.ForeignKey(Book, max_length=200, null=True, blank=True, on_delete = models.SET_NULL)
	created =  models.DateTimeField(auto_now_add=True) 

	def __str__(self):
		return self.product.title


# models.py
class ReadingProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    last_page = models.IntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.book} (Page {self.last_page})"

class BookNote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Highlight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    text = models.TextField()
    page = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    page = models.IntegerField()



class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="book_notifications"
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False) 