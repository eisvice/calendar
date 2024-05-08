import re
import calendar
import datetime
from decimal import Decimal
from django.urls import reverse
from .models import Theme, Event
from django.utils import timezone
from django.shortcuts import render
from .forms import ThemeForm, EventForm
from django.db.utils import IntegrityError
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST, require_GET


# Get JSON dates
def json_dates():
    context = []
    dates = Event.objects.all()
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
    return context


# Create your views here.
def index(request):
    theme_form = ThemeForm()
    event_form = EventForm()
    # TODO: add edit and delete buttons to themes tab
    themes = Theme.objects.all()
    context = {
        "theme_form": theme_form,
        "event_form": event_form,
        "themes": themes,
    }
    return render(request, "mnts/index.html", context)


def get_dates(request):
    context = json_dates()
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
        weekday_index = 0
        # TODO: add a constraint on the number of repetition in case when no weekdays were selcted!
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
    return HttpResponseRedirect(reverse("index"))

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
            context = {
                "themes": themes,
                "theme_form": ThemeForm(),
                "event_form": EventForm(),
            }
            return render(request, "mnts/settings-content.html", context)
        except IntegrityError:
            return render(request, "mnts/new-theme.html", {"theme_form": theme_form, "errors": "Create a unique theme"})
