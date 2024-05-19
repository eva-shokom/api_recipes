from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from foodgram.constants import (
    USERNAME_MAX_LENGTH, PASSWORD_MAX_LENGTH, STRING_MAX_LENGTH)


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

    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=[UnicodeUsernameValidator()],
        verbose_name='Логин',
        help_text=(
            f'Придумайте и введите логин. Допускается использование '
            f'строчных и заглавных букв, цифр, символов "@.+-_". '
            f'Максимальная длина логина - {USERNAME_MAX_LENGTH} символов.'
        ),
    )

    email = models.EmailField(
        unique=True,
        verbose_name='Email',
        help_text='Введите ваш адрес электронной почты',
    )

    password = models.CharField(
        max_length=PASSWORD_MAX_LENGTH,
        verbose_name='Пароль',
        help_text='Придумайте и введите пароль',
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
