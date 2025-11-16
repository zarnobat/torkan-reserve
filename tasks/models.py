from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Task(models.Model):
    class Priority(models.TextChoices):
        LOW = 'low', 'LOW'
        MEDIUM = 'medium', 'MEDIUM'
        HIGH = 'high', 'HIGH'

    class Status(models.TextChoices):
        TODO = 'todo', 'To Do'
        IN_PROGRESS = 'in_progress', 'In Progress'
        DONE = 'done', 'Done'
        CANCELLED = 'cancelled', 'Cancelled'

    creator = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='created_tasks',
    )
    assignee = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='assignee_tasks',
    )
    title = models.CharField(
        max_length=100,

    )
    description = models.TextField(
        null=True, blank=True 
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    priority = models.CharField(
        max_length=12,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.TODO,
    )
    category =  models.ForeignKey(
        'TaskCategory', 
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='tasks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', 'start_date']
        indexes = [
            models.Index(fields=['start_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.title
    
    @property
    def is_today(self):
        from datetime import date
        today = date.today()
        return (self.start_date == today) or (
            self.end_date and self.start_date <= today <= self.end_date
        )
    

class TaskCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_categories')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20, default='#2196F3') 

    def __str__(self):
        return self.name
