from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime


# Create your models here.
class User(AbstractUser):
    pass


class Theme(models.Model):
    name = models.CharField(max_length=30, unique=True)
    color = models.CharField(max_length=20)
    text_color = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"name: {self.name}, color: {self.color}, text_color: {self.text_color}"


class EventGroup(models.Model):
    name = models.CharField(max_length=20)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    total_days = models.PositiveIntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    weekdays = models.CharField(max_length=200, null=True, blank=True)
    
    def __str__(self):
        return f"name: {self.name}, total_days: {self.total_days}, theme: {self.theme.name}, start_date: {self.start_date}, end_date: {self.end_date}"
    

class Event(models.Model):
    number = models.PositiveIntegerField()
    event_group = models.ForeignKey(EventGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    start = models.DateTimeField()
    duration = models.TimeField(default=datetime.time(1, 0))
    end = models.DateTimeField()

    def __str__(self):
        return f"theme: {self.event_group.theme}, group_name: {self.event_group.name}, number: {self.number}, description: {self.description}, start: {self.start.isoformat()}, duration: {self.duration}, end: {self.end.isoformat()}"
    