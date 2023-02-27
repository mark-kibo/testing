from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, BookingForm
from django.utils import timezone
from datetime import datetime
from datetime import date
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet



# import our models for use
from .models import Location, ParkingSpace, Booking, ReserveUser

# Create your views here.

#get  hidden parameters

def billing_receipt(request, pk):
    obj = get_object_or_404(Booking, id=pk)
    print(obj.client, obj.check_in)
    

    # Get data for receipt
    name = f"{obj.client}"
    start_date = obj.check_in.strftime('%Y-%m-%d %H:%M:%S').split(" ")[0]
    end_date = obj.checkout.strftime('%Y-%m-%d %H:%M:%S').split(" ")[0]
    start_time = obj.check_in.strftime('%Y-%m-%d %H:%M:%S').split(" ")[1][:-3]
    end_time = obj.checkout.strftime('%Y-%m-%d %H:%M:%S').split(" ")[1][:-3]
    amount = obj.space.location.pricing_per_hour
    location=obj.space.location.name
    space=obj.space.name


    # Set colors
    blue_color = "#0066CC"
    dark_gray_color = "#333333"
    light_gray_color = "#CCCCCC"

     # Create data for table
    data = [
        
        ["Name","location", "space",  "Date in", "Date out", "Time in", "Time out","Amount"],
        [name, location, space, start_date, end_date, start_time, end_time,  f"${amount:.2f}"]]

      # Set style for title
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1

    # Create title for receipt
    title = Paragraph("Billing Receipt", title_style)

    # Set style for table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), blue_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, 1), light_gray_color),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 6),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ('WORDWRAP', (0, 0), (-1, -1), True),
        ('ROWBACKGROUNDS', (0, 0), (-1, 0), [dark_gray_color]),
    ])

    # Create PDF document
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="billing_receipt.pdf"'
    pdf_canvas = SimpleDocTemplate(response, pagesize=letter)

    # Create table and add data and style
    receipt_table = Table(data)
    receipt_table.setStyle(style)
    
    
    # Add table to PDF document
    elements = []
    elements.append(receipt_table)
    pdf_canvas.build(elements)

    return response


def create_spaces(request, location):
    Location_obj = get_object_or_404(Location, name=location)
    create_space(Location_obj, Location_obj.capacity)
    return redirect("home")


def index(request):
    if request.method == "POST":
        try:
            id_number = request.POST['id_no']
            plate_number = request.POST['plate']
            parking_location = request.POST['location']

            request.session['param1']=id_number
            request.session['param2']=plate_number
            location=get_object_or_404(Location, name=parking_location)
            if location:
                return redirect("spaces", parking_location)
            else:
                messages.info(request, f"No location named{parking_location}")
                return redirect("home")
        except Exception as e:
            messages.info(request, "{}".format(e))
            return redirect('/')
    else:
        spaces = Location.objects.all()
        return render(request, 'index.html', {'spaces': spaces})


def pricing(request):
    spaces = Location.objects.all()

    print(spaces)
    return render(request, 'pricing.html', {'spaces': spaces})


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


@login_required(login_url="login_user")
def bookings(request):
    client = ReserveUser.objects.get(username=request.user)
    booking = Booking.objects.filter(client=request.user).all()
    for book in booking:
        print(book)
    return render(request, 'bookings.html', {'booking': booking})


def login_user(request):
    if request.method == "POST":
        username = request.POST['name']
        password = request.POST['password']

        # authenticate our user

        user = authenticate(username=username, password=password)
        print(user.is_customer)
        if user.is_customer:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, "incorrect username or password")
            return redirect('login_user')
    return render(request, 'login.html')


def register_user(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            # get  form data
            name = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            # dont commit changes to allow an update
            update_data = form.save(commit=False)
            update_data.is_customer = True  # set user to customer
            update_data.save()
            print(name)
            # authenticate user
            user = authenticate(username=name, password=password)
            print(user)
            if user.is_customer:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, "failed to save")
                return redirect('register_user')
        else:
            messages.info(request, f"{form.errors}")
            return redirect('register_user')
    else:
        form = RegisterForm()
    return render(request, 'signup.html', {'form': form})


def parking_admin(request):
    return render(request, 'parking-admin/login.html')


def logout_user(request):
    logout(request)
    return redirect('home')


def spaces(request, parking_location):
    new=update_space_availability()
    print(new)
    location = get_object_or_404(Location, name=parking_location)
    print(location)
    spaces = ParkingSpace.objects.filter(location=location, is_booked=False)
    return render(request, "base.html", {'location': location, 'spaces': spaces})


def book(request, space_id):
    space = get_object_or_404(ParkingSpace, id=space_id)
    today = datetime.today()
    books= Booking.objects.filter(has_expired=False, checkout__date=today).first()
    print(books)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        print(form)
        if form.is_valid():
            check_in = form.cleaned_data['check_in']
            check_out = form.cleaned_data['checkout']
            if not space.is_available(check_in, check_out):
                # Space is not available for booking
                return render(request, 'base.html', {'space': space})
            # Create a new booking
            if books:
                messages.info(request, "you have an active booking")
                return redirect('bookings')
            else:
                booking = form.save(commit=False)
                booking.space = space
                booking.client = request.user
                booking.government_id=request.session.get('param1')
                booking.car_plate=request.session.get('param2')
                # Update space availability
                space.is_booked = True
                space.save()
                space.book(check_in, check_out)
                booking.save()
                messages.info(request, "book confirmed")
                # Redirect to the booking confirmation page
                return redirect('bookings')
    else:
        form = BookingForm()
        return render(request, 'book.html', {'space': space, 'form': form})


def create_space(location_obj, capacity):
    for i in range(capacity):
        space_name = f"{location_obj.name.split(' ')[0]} {i+1}"
        space = ParkingSpace(location=location_obj,
                             name=space_name, is_booked=False)
        space.save()


def update_space_availability():
    # get all the bookings for today
    today = date.today()
    bookings = Booking.objects.filter(
        checkout__gte=timezone.now(), check_in__date=today)

    # update the is_booked field of the corresponding spaces to False if the time is expired
    for booking in bookings:
        print(booking.checkout.strftime('%Y-%m-%d %H:%M:%S') , datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        print(f"{booking.is_expired()} printed")
        print(booking.checkout.strftime('%Y-%m-%d %H:%M:%S') < datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        if booking.is_expired():
            booking.space.is_booked = False
            booking.space.save()
            booking.has_expired = True
            booking.save()
            print(f"")

def delete_booking(request, pk):
    Book_obj=get_object_or_404(Booking, id=pk)
    Book_obj.delete()
    return redirect('bookings')


def update(request, pk):
    obj=get_object_or_404(Booking, id=pk)
    
    if request.method == "POST":
        form = BookingForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.info(request, f'{obj} updated')
            return redirect("bookings")
    else:
        form = BookingForm(instance=obj)
        return render(request, "update.html", {'form':form})
