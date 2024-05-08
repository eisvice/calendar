from django import forms
from .models import Theme
from django.utils import timezone


class EventChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name
    

class CustomDateTimeWidget(forms.DateTimeInput):
    input_type = 'datetime-local'


class CustomTimeWidget(forms.TimeInput):
    input_type = 'time'


class ThemeForm(forms.Form):
    name = forms.CharField(label="Theme", max_length=30)
    color = forms.CharField(label="Background Color", max_length=10)
    text_color = forms.CharField(label="Text Color", max_length=10)


class EventForm(forms.Form):
    theme = EventChoiceField(label="Choose Theme", queryset=Theme.objects.all(), to_field_name="name", required=True)
    title = forms.CharField(label="Event Title", max_length=20)
    description = forms.CharField(label="Description")
    start = forms.DateTimeField(label="Start Time", widget=CustomDateTimeWidget(format='%Y-%m-%d %H:%M'))
    duration = forms.TimeField(label="Event Duration", initial="01:00", widget=CustomTimeWidget)
    repeats = forms.IntegerField(initial=1, min_value=1)
