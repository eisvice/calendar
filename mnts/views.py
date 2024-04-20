import calendar
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Theme, Event

# Create your views here.
def index(request):
    weekdays = calendar.weekheader(10).split()
    context = {
        "weekdays": weekdays,
        "hours": range(24)
    }
    return render(request, "mnts/index.html", context)

def get_dates(request):
    print(request.GET)
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

    return JsonResponse(context, safe=False)