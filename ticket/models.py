import uuid
from django.db import models
from users.models import User,Department


class Ticket(models.Model):
    status_choices = (
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('Pending', 'Pending'),
    )

    type_choices = (
        ('print', 'Принтер'),
        ('computer', 'Компьютер'),
        ('bars', 'БАРС'),
        ('internet', 'Интернет'),
        ('mounting', 'Установка оборудования'),
    )

    ticket_number = models.UUIDField(default=uuid.uuid4)
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by')
    date_created = models.DateTimeField(auto_now_add=True)
    assigned_to = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    is_resolved = models.BooleanField(default=False)
    closed_date = models.DateTimeField(null=True, blank=True)
    ticket_status = models.CharField(max_length=20, choices=status_choices)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True)
    ticket_type = models.CharField(max_length=30, choices=type_choices)

    def __str__(self):
        return self.title
