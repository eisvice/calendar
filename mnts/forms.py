from django import forms
from .models import Theme
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Password Confirmation'
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        self.fields['username'].help_text = None
        self.fields['email'].widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            'username': forms.TextInput(attrs={'autocomplete': 'off'}),
        }


class EventChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name
    

class CustomDateTimeWidget(forms.DateTimeInput):
    input_type = 'datetime-local'


class CustomTimeWidget(forms.TimeInput):
    input_type = 'time'


class ThemeForm(forms.ModelForm):
    name = forms.CharField(label="Theme", max_length=30)
    color = forms.CharField(label="Background Color", max_length=7)
    text_color = forms.CharField(label="Text Color", max_length=7)

    class Meta:
        model = Theme
        fields = ("name", "color", "text_color",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            self.fields['name'].widget.attrs.update({'id': f'edit-name-{instance.id}'})
            self.fields['color'].widget.attrs.update({'id': f'edit-color-{instance.id}'})
            self.fields['text_color'].widget.attrs.update({'id': f'edit-text-color-{instance.id}'})


class EventForm(forms.Form):
    theme = EventChoiceField(label="Choose Theme", queryset=Theme.objects.all(), to_field_name="name", required=True)
    title = forms.CharField(label="Event Title", max_length=20)
    description = forms.CharField(label="Description")
    start = forms.DateTimeField(label="Start Time", widget=CustomDateTimeWidget(format='%Y-%m-%d %H:%M'))
    duration = forms.TimeField(label="Event Duration", initial="01:00", widget=CustomTimeWidget)
    repeats = forms.IntegerField(initial=1, min_value=1)
