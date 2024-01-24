from django.shortcuts import render, redirect
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from django.http import HttpResponseRedirect
from .models import Event, Venue
from .forms import VenueForm, EventForm
from django.http import HttpResponse
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