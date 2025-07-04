from django.db import models

from django.contrib.auth.models import User





class Task(models.Model):
    class Status(models.TextChoices):
        NEW = 'nowy', 'Nowy'
        IN_PROGRESS = 'w_toku', 'W toku'
        RESOLVED = 'rozwiazany', 'Rozwiązany'

    # nazwa
    name = models.CharField(max_length=255)
    # opis
    description = models.TextField(blank=True, null=True)
    # status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW
    )
    # przypisany użytkownik
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    # data utworzenia i aktualizacji
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.status})"



class TaskHistory(models.Model):
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, related_name='history')
    task_id_snapshot = models.IntegerField(null=True, blank=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_by_username = models.CharField(max_length=150, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    field = models.CharField(max_length=255)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.task.name} - {self.field} zmienione przez {self.changed_by} w {self.timestamp}"
