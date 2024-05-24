import random
import string

from django.db import models

from foodgram.constants import LINK_LENGTH, MAX_LENGTH, MAX_LINK_LENGTH


class Link(models.Model):
    """Модель для коротких ссылок."""
    full_url = models.CharField(max_length=MAX_LENGTH)
    short_url = models.CharField(
        max_length=MAX_LINK_LENGTH, unique=True)

    class Meta:
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'

    def save(self, *args, **kwargs):
        """Метод для автоматической генерации уникальной короткой ссылки."""
        while not self.short_url and not Link.objects.filter(
                short_url=self.short_url).exists():
            self.short_url = ''.join(
                random.choices(
                    string.ascii_letters + string.digits,
                    k=LINK_LENGTH
                )
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.short_url
