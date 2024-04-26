from django.db import models

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
    end = models.DateTimeField()

    def __str__(self):
        return f"theme: {self.theme}, title: {self.title}, description: {self.description}, start: {self.start.isoformat()}, end: {self.end.isoformat()}"