import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField('Имя', help_text='Введите имя', max_length=150)
    last_name = models.CharField('Фамилия', help_text='Ведите фамилию', max_length=150)
    created_date = models.DateTimeField('Дата регистрации', auto_now_add=True)

    class Meta:
        ordering = ('id',)
        verbose_name = 'Упаковщики'
        verbose_name_plural = 'Упаковщики'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
