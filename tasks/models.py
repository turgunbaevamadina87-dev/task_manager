from django.db import models

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Task(models.Model):

    class Status(models.TextChoices):
        TODO = "todo", "To Do"
        IN_PROGRESS = "In progress", "In Progress"
        DONE = "done", "Done"

    title = models.CharField(
        max_length=255,
        verbose_name="Title"
    )

    description = models.TextField(
        verbose_name="Description"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO
    )

    deadline = models.DateField()

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tasks"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.title} ({self.owner.username})"

    class Meta:
        ordering = ["-created_at"]
