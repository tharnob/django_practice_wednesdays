from django.shortcuts import render
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from django.http import HttpResponseRedirect
from .models import Event
from .forms import VenueForm

# Create your views here.


def add_venue(request):

    submitted = False
    if request.method == "POST":
        form = VenueForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/add_venue?submitted=True')
    else:
        form = VenueForm
        if 'submitted' in request.GET:
            submitted = True



    context = {
        'form' : form,
        'submitted' : submitted,
    }
    return render(request, 'add_venue.html', context)




def home(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
    name = "Arnob"
    month = month.capitalize()

    # Convert month from name to number
    month_number = list(calendar.month_name).index(month)
    month_number = int(month_number)

    # Create calendar
    cal = HTMLCalendar().formatmonth(year, month_number)

    # Get current year
    now = datetime.now()
    current_year = now.year

    # Get current time
    time = now.strftime('%I:%M:%S %p')

    context = {
        "name" : name,
        "year" : year,
        "month" : month,
        "month_number" : month_number,
        "cal" : cal,
        "current_year" : current_year,
        "time" : time,
    }
    return render(request, 'home.html', context)




def all_events(request):
    event_list = Event.objects.all()
    context = {
        "event_list" : event_list,
    }
    return render(request, 'event_list.html', context)