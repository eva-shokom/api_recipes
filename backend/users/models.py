from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.constants import (
    USERNAME_MAX_LENGTH, STRING_MAX_LENGTH)


class User(AbstractUser):
    """ Кастомная модель пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    first_name = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        verbose_name='Имя',
        help_text='Введите ваше имя'
    )

    last_name = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        verbose_name='Фамилия',
        help_text='Введите вашу фамилию'
    )

    email = models.EmailField(
        unique=True,
        verbose_name='Email',
        help_text='Введите ваш адрес электронной почты',
    )

    avatar = models.ImageField(
        upload_to='users/images/',
        null=True,
        verbose_name='Аватар пользователя'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username[:STRING_MAX_LENGTH]
