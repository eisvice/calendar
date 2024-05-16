import re
import datetime
from dateutil.parser import parse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import User, Theme, EventGroup, Event
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.contrib.auth.views import PasswordChangeView, PasswordResetView
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView
from django.utils import timezone
from django.shortcuts import render
from .forms import ThemeForm, EventForm, SignUpForm
from django.http.request import QueryDict
from django.db.utils import IntegrityError
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST, require_GET


class UserRegisterView(CreateView):
    form_class = SignUpForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")


class ChangePasswordView(PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = "registration/change-password.html"
    success_url = reverse_lazy("login")


class ResetPasswordView(PasswordResetView):
    form_class = PasswordResetForm
    template_name = "registration/reset-password.html"
    success_url = reverse_lazy("password_reset_done")


# Create your views here.
@login_required
def index(request):
    theme_form = ThemeForm()
    event_form = EventForm()
    themes = Theme.objects.all()
    theme_forms = [ThemeForm(instance=theme) for theme in themes]
    themes_and_forms = zip(themes, theme_forms)
    context = {
        "theme_form": theme_form,
        "event_form": event_form,
        "themes_and_forms": themes_and_forms,
    }
    return render(request, "mnts/index.html", context)


def get_dates(request):
    print(request.GET)
    start_str = request.GET.get("start")
    end_str = request.GET.get("end")
    start = parse(start_str)
    end = parse(end_str)
    print(start, end, type(start), type(end))
    # print(timezone.is_aware(start), timezone.is_aware())
    context = []
    dates = Event.objects.filter(start__range=(start, end))
    for date in dates:
        context.append(
            {
                'id': date.id,
                'title':date.title,
                'description':date.description,
                'start':date.start.isoformat(),
                'hours':f"{date.duration}",
                'end':date.end.isoformat(),
                'color':date.theme.color,
                'textColor':date.theme.text_color
            }
        )
    return JsonResponse(context, safe=False)


@require_POST
def add_event(request):
    event_form = EventForm(request.POST)
    weekdays = {}
    if event_form.is_valid():
        data = event_form.cleaned_data
        current_tz = timezone.get_current_timezone()
        theme = data["theme"]
        title = data["title"]
        description = data["description"]
        start = data["start"]
        duration_datetime = data["duration"]
        duration = duration_datetime.hour * 60 + duration_datetime.minute
        repeats = int(data["repeats"])
        for key in request.POST:
            if re.search(r"time-\w+", key):
                weekdays |= {int(key.replace("time-", "")): request.POST.get(key)}
        if repeats > 1 and len(weekdays) == 0:
            return render(request, "mnts/new-event.html", {"event_form": event_form, "error": "Check some of the weekdays to assign more than 1 day"}, status=422)
        weekday_index = 0
        current_day = start
        while weekday_index < repeats:
            if current_day == start or current_day.weekday() in weekdays:
                if current_day == start:
                    start_time = start
                else:
                    start_time = timezone.make_aware(datetime.datetime.combine(current_day.date(), datetime.datetime.strptime(weekdays[current_day.weekday()], '%H:%M').time()))
                new_event = Event.objects.create(
                    theme=theme,
                    title=f"{title} #{weekday_index+1}",
                    description=description,
                    start=start_time.astimezone(current_tz),
                    duration = duration_datetime,
                    end=start_time+datetime.timedelta(minutes=duration),
                )
                new_event.save()
                weekday_index += 1
            current_day += datetime.timedelta(days=1)
        return render(request, "mnts/new-event.html", {"event_form": EventForm()})


@require_POST
def edit_event(request):
    data = request.POST
    id = int(data.get("event-id"))
    new_date = datetime.datetime.fromisoformat(data.get("new-start-time"))
    new_duration_datetime = datetime.time.fromisoformat(data.get("new-duration"))
    new_duration = new_duration_datetime.hour * 60 + new_duration_datetime.minute
    event = Event.objects.get(pk=id)
    event.start = timezone.make_aware(new_date)
    event.duration = new_duration_datetime
    event.end = timezone.make_aware(new_date + datetime.timedelta(minutes=new_duration))
    event.save(update_fields=["start", "duration", "end"])
    return HttpResponse()


@require_POST
def add_theme(request):
    theme_form = ThemeForm(request.POST)
    if theme_form.is_valid():
        try:
            data = theme_form.cleaned_data
            name = data["name"]
            color = data["color"]
            text_color = data["text_color"]
            theme = Theme.objects.create(name=name, color=color, text_color=text_color)
            theme.save()
            themes = Theme.objects.all()
            theme_forms = [ThemeForm(instance=theme) for theme in themes]
            themes_and_forms = zip(themes, theme_forms)
            context = {
                "theme_form": ThemeForm(),
                "event_form": EventForm(),
                "themes_and_forms": themes_and_forms,
            }
            return render(request, "mnts/settings-content.html", context)
        except IntegrityError:
            return render(request, "mnts/new-theme.html", {"theme_form": theme_form, "errors": "Create a unique theme"})
        

def edit_theme(request, id):
    theme = Theme.objects.get(pk=id)
    if request.method == "DELETE":
        theme.delete()
        return HttpResponse("theme was deleted")
    elif request.method == "PATCH":
        data = QueryDict(request.body)
        print(data)
        theme_form = ThemeForm(data, instance=theme)
        if theme_form.is_valid():
            theme_form.save()
            return render(request, "mnts/theme-row.html", {"form": ThemeForm(instance=theme), "theme": theme})