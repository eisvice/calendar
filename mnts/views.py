import re
import calendar
import datetime
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
                'title':date.title,
                'description':date.description,
                'start':date.start.isoformat(),
                'end':date.end.isoformat(),
                'color':date.theme.color,
                'textColor':date.theme.text_color
            }
        )
    return context


# Create your views here.
def index(request):
    weekdays = calendar.weekheader(10).split()
    theme_form = ThemeForm()
    event_form = EventForm()
    themes = Theme.objects.all()
    context = {
        "weekdays": weekdays,
        "hours": range(24),
        "theme_form": theme_form,
        "event_form": event_form,
        "themes": themes,
    }
    return render(request, "mnts/index.html", context)


def get_dates(request):
    print(request.GET)
    context = json_dates()
    return JsonResponse(context, safe=False)


@require_POST
def add_event(request):
    print(request.POST)
    event_form = EventForm(request.POST)
    weekdays = {}
    if event_form.is_valid():
        print("valid event form")
        print(event_form.cleaned_data)
        data = event_form.cleaned_data
        current_tz = timezone.get_current_timezone()
        theme = data["theme"]
        title = data["title"]
        description = data["description"]
        start = data["start"]
        repeats = int(data["repeats"])
        for key in request.POST:
            if re.search(r"time-\w+", key):
                print("FOUND", key, request.POST.get(key))
                weekdays |= {int(key.replace("time-", "")): request.POST.get(key)}
        print(weekdays)
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
                    end=start_time+datetime.timedelta(hours=1),
                )
                new_event.save()
                print(new_event)
                print("current", current_tz)
                weekday_index += 1
            current_day += datetime.timedelta(days=1)
        # get_dates(request)
        return render(request, "mnts/new-event.html", {"event_form": EventForm()})


@require_POST
def add_theme(request):
    print(request.POST)
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
            themes = render_to_string("mnts/theme-oob.html", {"themes": themes})
            new_theme = render_to_string("mnts/new-theme.html", {"theme_form": ThemeForm()}, request=request)
            return HttpResponse(themes + new_theme)
        except IntegrityError:
            return render(request, "mnts/new-theme.html", {"theme_form": theme_form, "errors": "Create a unique theme"})
