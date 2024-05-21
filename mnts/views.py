import re
import datetime
import calendar
from dateutil.parser import parse
from django.contrib.auth.decorators import login_required
from .models import User, Theme, EventGroup, Event
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.contrib.auth.views import PasswordChangeView, PasswordResetView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from .forms import ThemeForm, EventForm, SignUpForm
from django.http.request import QueryDict
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest
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


@login_required
def index(request):
    theme_form = ThemeForm()
    event_form = EventForm()
    themes = Theme.objects.filter(user=request.user)
    theme_forms = [ThemeForm(instance=theme) for theme in themes]
    themes_and_forms = zip(themes, theme_forms)
    event_groups = EventGroup.objects.filter(theme__id__in=themes).order_by("id")
    context = {
        "event_form": event_form,
        "event_groups": event_groups,
        "themes_and_forms": themes_and_forms,
        "theme_form": theme_form,
        "themes_count": themes.count(),
        "currentTab": "Themes",
    }
    return render(request, "mnts/index.html", context)

@login_required
def get_dates(request):
    start_str = request.GET.get("start")
    end_str = request.GET.get("end")
    start = parse(start_str)
    end = parse(end_str)
    context = []
    dates = Event.objects.filter(user=request.user, start__range=(start, end))
    for date in dates:
        context.append(
            {
                'id': date.id,
                'title':f"{date.event_group.name} #{date.number}",
                'description':date.description,
                'start':date.start.isoformat(),
                'hours':f"{date.duration}",
                'end':date.end.isoformat(),
                'color':date.event_group.theme.color,
                'textColor':date.event_group.theme.text_color
            }
        )
    return JsonResponse(context, safe=False)


@require_POST
@login_required
def add_event(request):
    print(request.headers)
    event_form = EventForm(request.POST)
    weekdays = {}
    weekdays_str = ""
    if event_form.is_valid():
        data = event_form.cleaned_data
        current_tz = timezone.get_current_timezone()
        theme = data["theme"]

        if Theme.objects.filter(pk=theme.id).exists() == False:
            event_form.add_error("theme", "The theme doesn't exist")
            context = {
                "event_form": event_form,
            }
            return render(request, "mnts/new-event-form.html", context, status=422)
        
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
            event_form.add_error(None, "Check some of the weekdays to assign more than 1 day")
            context = {
                "event_form": event_form
            }
            return render(request, "mnts/new-event-form.html", context, status=422)
        
        new_event_group = EventGroup.objects.create(
            name = title,
            theme = Theme.objects.get(pk=theme.id),
            total_days = repeats,
            start_date = start,
        )
        weekday_index = 0
        current_day = start
        while weekday_index < repeats:
            if current_day == start or current_day.weekday() in weekdays:
                if current_day.weekday() in weekdays and str(calendar.day_name[current_day.weekday()]) not in weekdays_str:
                    weekdays_str += f"{calendar.day_name[current_day.weekday()]} "
                if current_day == start:
                    start_time = start
                else:
                    start_time = timezone.make_aware(datetime.datetime.combine(current_day.date(), datetime.datetime.strptime(weekdays[current_day.weekday()], '%H:%M').time()))

                new_event = Event.objects.create(
                    number=weekday_index+1,
                    event_group=new_event_group,
                    user=request.user,
                    description=description,
                    start=start_time.astimezone(current_tz),
                    duration = duration_datetime,
                    end=start_time+datetime.timedelta(minutes=duration),
                )
                new_event.save()

                if weekday_index == repeats - 1:
                    new_event_group.weekdays = weekdays_str
                    new_event_group.end_date = start_time.astimezone(current_tz)
                    new_event_group.save(update_fields=["weekdays", "end_date"])
                weekday_index += 1
            current_day += datetime.timedelta(days=1)
        themes = Theme.objects.filter(user=request.user)
        theme_forms = [ThemeForm(instance=theme) for theme in themes]
        themes_and_forms = zip(themes, theme_forms)
        event_groups = EventGroup.objects.filter(theme__id__in=themes).order_by("id")
        context = {
            "event_form": EventForm(),
            "theme_form": ThemeForm(),
            "themes_and_forms": themes_and_forms,
            "event_groups": event_groups,
            "themes_count": themes.count(),
        }
        return render(request, "mnts/event-settings.html", context, status=200)
    else:
        context = {"event_form": event_form}
        return render(request, "mnts/new-event-form.html", context, status=422)


@login_required
def event_group(request, id):
    event_group = EventGroup.objects.get(pk=id)
    if event_group.theme.user == request.user:
        if request.method == "DELETE":
            event_group.delete()
            return HttpResponse("event group was deleted")
        else:
            return HttpResponseBadRequest()
    else:
        return HttpResponseNotAllowed()


@require_POST
@login_required
def edit_event(request):
    data = request.POST
    id = int(data.get("event-id"))
    new_date = datetime.datetime.fromisoformat(data.get("new-start-time"))
    new_duration_datetime = datetime.time.fromisoformat(data.get("new-duration"))
    new_duration = new_duration_datetime.hour * 60 + new_duration_datetime.minute
    event = get_object_or_404(Event, pk=id)
    if event.user == request.user:
        event.start = timezone.make_aware(new_date)
        event.duration = new_duration_datetime
        event.end = timezone.make_aware(new_date + datetime.timedelta(minutes=new_duration))
        event.save(update_fields=["start", "duration", "end"])
        return HttpResponse()
    else:
        return HttpResponseNotAllowed()


@require_POST
@login_required
def add_theme(request):
    post_data = request.POST.copy()  # Make a mutable copy of the POST data
    post_data.update({'user': request.user})  # Add the user id to the POST data
    theme_form = ThemeForm(post_data)
    if theme_form.is_valid():
        theme_form.save()
        themes = Theme.objects.filter(user=request.user)
        theme_forms = [ThemeForm(instance=theme) for theme in themes]
        themes_and_forms = zip(themes, theme_forms)
        event_groups = EventGroup.objects.filter(theme__id__in=themes).order_by("id")
        context = {
            "theme_form": ThemeForm(),
            "event_form": EventForm(),
            "themes_and_forms": themes_and_forms,
            "event_groups": event_groups,
            "themes_count": themes.count(),
        }
        return render(request, "mnts/event-settings.html", context, status=200)
    else:
        context = {"theme_form": theme_form}
        return render(request, "mnts/new-theme-form.html", context, status=422)
        

@login_required
def edit_theme(request, id):
    theme = Theme.objects.get(pk=id)
    if theme.user == request.user:
        if request.method == "DELETE":
            theme.delete()
        elif request.method == "PATCH":
            data = QueryDict(request.body).copy()
            data.update({'user': request.user})
            theme_form = ThemeForm(data, instance=theme)
            if theme_form.is_valid():
                theme_form.save()
            else:
                context = {"form": theme_form, "theme": theme}
                return render(request, "mnts/theme-row-form.html", context, status=422)
        else:
            return HttpResponseBadRequest()
        themes = Theme.objects.filter(user=request.user)
        theme_forms = [ThemeForm(instance=theme) for theme in themes]
        themes_and_forms = zip(themes, theme_forms)
        event_groups = EventGroup.objects.filter(theme__id__in=themes).order_by("id")
        context = {
            "theme_form": ThemeForm(),
            "event_form": EventForm(),
            "themes_and_forms": themes_and_forms,
            "event_groups": event_groups,
            "themes_count": themes.count(),
        }
        return render(request, "mnts/event-settings.html", context, status=200)
    else:
        return HttpResponseNotAllowed()
