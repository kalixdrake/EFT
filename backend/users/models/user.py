from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = 'client', 'Client'
        EMPLOYEE = 'employee', 'Employee'
        ADMIN = 'admin', 'Admin'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT)
    phone = models.CharField(max_length=20, blank=True)
    document_type = models.CharField(max_length=30, blank=True)
    document_number = models.CharField(max_length=50, blank=True)
    email = models.EmailField(unique=True)

    def save(self, *args, **kwargs):
        if self.email and not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    @property
    def is_privileged(self):
        return self.role in {self.Role.EMPLOYEE, self.Role.ADMIN} or self.is_staff or self.is_superuser