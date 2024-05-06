from django.db import models
import datetime

# Create your models here.
class Theme(models.Model):
    name = models.CharField(max_length=30, unique=True)
    color = models.CharField(max_length=20)
    text_color = models.CharField(max_length=20)

    def __str__(self):
        return f"name: {self.name}, color: {self.color}, text_color: {self.text_color}"


class Event(models.Model):
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    title = models.CharField(max_length=20)
    description = models.TextField()
    start = models.DateTimeField()
    duration = models.TimeField(default=datetime.time(1, 0))
    end = models.DateTimeField()

    def __str__(self):
        return f"theme: {self.theme}, title: {self.title}, description: {self.description}, start: {self.start.isoformat()}, duration: {self.duration}, end: {self.end.isoformat()}"