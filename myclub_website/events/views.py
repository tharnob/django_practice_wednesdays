from django.shortcuts import render, redirect
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from django.http import HttpResponseRedirect
from .models import Event, Venue
# Importing user model from django
from django.contrib.auth.models import User
from .forms import VenueForm, EventForm, EventFormAdmin
from django.http import HttpResponse
from django.contrib import messages
import csv

# For PDF
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

# Import pagination stuff
from django.core.paginator import Paginator


# Create your views here.

def venue_events(request, venue_id):
    # Grab the venue
    venue = Venue.objects.get(id=venue_id)
    # Grab the events from that venue
    events = venue.event_set.all()
    context = {
        "events" : events,
    }
    if events:
        return render(request, 'venue_events.html', context)
    else:
        messages.success(request, ("That Venue Has No Events At This Time..."))
        return redirect('admin-approval')



# Show Event
def show_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    context = {
        "event" : event,
    }
    return render(request, 'show_event.html', context)




# Show Events In A Venue
def admin_approval(request):
    # Get The Venues
    venue_list = Venue.objects.all()
    # Get Counts
    event_count = Event.objects.all().count()
    venue_count = Venue.objects.all().count()
    user_count = User.objects.all().count()

    event_list = Event.objects.all().order_by("-event_date")
    context = {
        "event_list" : event_list,
        "event_count" : event_count,
        "venue_count" : venue_count,
        "user_count" : user_count,
        "venue_list" : venue_list,
    }
    if request.user.is_superuser:
        if request.method == "POST":
            id_list = request.POST.getlist('boxes')
            
            # Uncheck all events.
            # Because uncheck don't return any value like check is True 
            event_list.update(approved=False)

            # Update the database
            for x in id_list:
                Event.objects.filter(pk=int(x)).update(approved=True)


            messages.success(request, ("Event List Approval Has Been Updated!"))
            return redirect('list-events')
        else:
            return render(request, "admin_approval.html", context)
    else:
        messages.success(request, ("You aren't authorized to view this page!"))
        return redirect('home')


    return render(request, "admin_approval.html", context)



def search_events(request):
    if request.method == "POST":
        searched = request.POST['searched']
        events = Event.objects.filter(description__contains=searched)
        context = {
            "searched" : searched,
            "events" : events,
        }
        return render(request, 'search_events.html', context)
    else:
        return render(request, 'search_events.html', {}) 



def my_events(request):
    me = request.user.id
    events = Event.objects.filter(attendees = me)
    context = {
        "events" : events,

    }
    if request.user.is_authenticated:
        return render(request, 'my_events.html', context)
    else:
        messages.success(request, ("You Aren't Authorized To View This Page!"))
        return redirect('home')





# Have to pip install  reportlab for pdf, because django or python does not have this
# Generate pdf file venue list
def venue_pdf(request):
    # Create a Bytestream buffer
    buf = io.BytesIO()
    # Create a Canvas
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    # Create a text object
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)

    # Add some lines of text
    # lines = [
    #     "This is line 1",
    #     "This is line 1",
    #     "This is line 1",
    # ]

    # Designate the model
    venues = Venue.objects.all()

    lines = []
    for venue in venues:
        lines.append(venue.name)
        lines.append(venue.address)
        lines.append(venue.zip_code)
        lines.append(venue.phone)
        lines.append(venue.web)
        lines.append(venue.email_address)
        lines.append("====================")


    for line in lines:
        textob.textLine(line)

    
    # Finish up
    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename="venue.pdf")







# Generate csv file venue list
def venue_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=venues.csv'

    # Create a CSV writer
    writer = csv.writer(response)

    # Designate the model
    venues = Venue.objects.all()

    # Add column headings to the CSV file
    writer.writerow(['Venue Name', 'Address', 'Zip Code', 'Phone', 'Web Address', 'Email'])

    for venue in venues:
        writer.writerow([venue.name, venue.address, venue.zip_code, venue.phone, venue.web, venue.email_address])
    
    return response




# Generate text file venue list
def venue_text(request):
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=venues.txt'

    # Designate the model

    venues = Venue.objects.all()
    lines = []
    for venue in venues:
        lines.append(f'{venue.name}\n{venue.address}\n{venue.zip_code}\n{venue.phone}\n{venue.web}\n{venue.email_address}\n\n\n')

    #lines = ['This is line 1\n', 'This is line 3\n', 'This is line 3\n']

    # Write to textfile
    response.writelines(lines)
    return response



def delete_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    venue.delete()
    return redirect('list-venues')


def delete_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    if request.user == event.manager:
        event.delete()
        messages.success(request, ("Event Deleted!"))
        return redirect('list-events')
    else:
        messages.success(request, ("You Aren't Authorized To Delete This Event!"))
        return redirect('list-events')





def update_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    if request.user.is_superuser:
        form = EventFormAdmin(request.POST or None, instance=event)
    else:
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
        if request.user.is_superuser:
            form = EventFormAdmin(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/add_event?submitted=True')
        else:
            form = EventForm(request.POST)
            if form.is_valid():
                event = form.save(commit=False) # save but not yet, wait
                event.manager = request.user # Logged in user
                event.save()
                #form.save()
                return HttpResponseRedirect('/add_event?submitted=True')
    else:
        # Just going to the page, not submitting
        if request.user.is_superuser:
            form = EventFormAdmin
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
    form = VenueForm(request.POST or None, request.FILES or None, instance=venue)
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
    venue_owner = User.objects.get(pk=venue.owner)
    context = {
        "venue" : venue,
        "venue_owner" : venue_owner,
    }
    return render(request, 'show_venue.html', context)



def list_venues(request):
    #venue_list = Venue.objects.all().order_by('?') #randomize order
    venue_list = Venue.objects.all()

    # Set up paginaion
    p = Paginator(Venue.objects.all(), 2)
    page = request.GET.get('page')
    venues = p.get_page(page)
    nums = "a" * venues.paginator.num_pages

    context = {
        "venue_list" : venue_list,
        "venues" : venues,
        "nums" : nums,
    }
    return render(request, 'venues.html', context)


def add_venue(request):

    submitted = False
    if request.method == "POST":
        form = VenueForm(request.POST, request.FILES)
        if form.is_valid():
            # Saving something in the field without user input
            venue = form.save(commit=False) # save but not yet
            venue.owner = request.user.id # Logged in user
            venue.save()
            #form.save()
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

    # Query The Events Model For Dates
    event_list = Event.objects.filter(
        event_date__year = year,
        event_date__month = month_number
        )

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
        "event_list" : event_list,
    }
    return render(request, 'home.html', context)




def all_events(request):
    event_list = Event.objects.all().order_by('-event_date', 'name')
    context = {
        "event_list" : event_list,
    }
    return render(request, 'event_list.html', context)