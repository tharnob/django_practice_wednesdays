from django.shortcuts import render, redirect
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from django.http import HttpResponseRedirect
from .models import Event, Venue
from .forms import VenueForm, EventForm

# Create your views here.

def delete_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    venue.delete()
    return redirect('list-venues')


def delete_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    event.delete()
    return redirect('list-events')



def update_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    form = EventForm(request.POST or None, instance=event)
    if form.is_valid():
        form.save()
        return redirect('list-events')
    context = {
        "event" : event,
        "form" : form,
    }
    return render(request, 'update_event.html', context)


def add_event(request):

    submitted = False
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/add_event?submitted=True')
    else:
        form = EventForm
        if 'submitted' in request.GET:
            submitted = True

    context = {
        'form' : form,
        'submitted' : submitted,
    }
    return render(request, 'add_event.html', context)




def update_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    form = VenueForm(request.POST or None, instance=venue)
    if form.is_valid():
        form.save()
        return redirect('list-venues')
    context = {
        "venue" : venue,
        "form" : form,
    }
    return render(request, 'update_venue.html', context)



def search_venues(request):
    if request.method == "POST":
        searched = request.POST['searched']
        venues = Venue.objects.filter(name__contains=searched)
        context = {
            "searched" : searched,
            "venues" : venues,
        }
        return render(request, 'search_venues.html', context)
    else:
        return render(request, 'search_venues.html', {})        



def show_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    context = {
        "venue" : venue,
    }
    return render(request, 'show_venue.html', context)



def list_venues(request):
    venue_list = Venue.objects.all().order_by('?') #randomize order
    context = {
        "venue_list" : venue_list,
    }
    return render(request, 'venues.html', context)


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
    event_list = Event.objects.all().order_by('event_date', 'name')
    context = {
        "event_list" : event_list,
    }
    return render(request, 'event_list.html', context)