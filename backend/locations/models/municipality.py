from django.db import models

from .department import Department


class Municipality(models.Model):
    department = models.ForeignKey(Department, related_name='municipalities', on_delete=models.CASCADE)
    name = models.CharField(max_length=120)

    class Meta:
        ordering = ['name']
        verbose_name = 'Municipality'
        verbose_name_plural = 'Municipalities'
        constraints = [
            models.UniqueConstraint(fields=['department', 'name'], name='unique_municipality_per_department'),
        ]

    def __str__(self):
        return f'{self.name}, {self.department.name}'
