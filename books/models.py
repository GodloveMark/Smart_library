
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
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    last_page = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'book'],
                name='unique_user_book_progress'
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.book} (Page {self.last_page})"


class BookNote(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    note = models.TextField()
    page = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.book.title} - Page {self.page}"


class Highlight(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    text = models.TextField()
    page = models.PositiveIntegerField(default=1)

    # Highlight appearance and PDF positioning
    color = models.CharField(max_length=20, default='#FFE66D')
    position_data = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.book.title} - Highlight Page {self.page}"


class Bookmark(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    page = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'book', 'page'],
                name='unique_user_bookmark_page'
            )
        ]

    def __str__(self):
        return f"{self.book.title} - Page {self.page}"


class BookAnnotation(models.Model):
    ANNOTATION_TYPES = [
        ('pencil', 'Pencil Drawing'),
        ('underline', 'Underline'),
        ('shape', 'Shape'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    page = models.PositiveIntegerField(default=1)

    annotation_type = models.CharField(
        max_length=20,
        choices=ANNOTATION_TYPES
    )

    color = models.CharField(max_length=20, default='#FF0000')
    position_data = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return (
            f"{self.user} - {self.book.title} "
            f"- {self.annotation_type} - Page {self.page}"
        )




class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="book_notifications"
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False) 