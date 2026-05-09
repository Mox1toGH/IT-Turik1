from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class NewsArticle(models.Model):
    title = models.CharField(max_length=255)
    content = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='created_news_articles',
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.title

    def clean(self):
        if self.content is not None and not isinstance(self.content, dict):
            raise ValidationError({'content': 'Content must be a JSON object (dict).'})

