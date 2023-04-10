from django.db import models
from django.contrib.auth.models import AbstractUser


class Department(models.Model):
    name = models.CharField(max_length=255, verbose_name='Отдел')

    def __str__(self):
        return self.name


class User(AbstractUser):
    is_customer = models.BooleanField(default=False)
    is_engineer = models.BooleanField(default=False)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, verbose_name='Отдел', null=True)

    def __str__(self):
        return self.username


