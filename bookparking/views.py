from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, BookingForm
from django.utils import timezone
from datetime import datetime
from datetime import date

# import our models for use
from .models import Location, ParkingSpace, Booking, ReserveUser

# Create your views here.


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

            return redirect("spaces", parking_location)
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
        print(user)
        if user and user.is_customer:
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
            if user and user.is_customer:
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
    return render(request, 'register.html', {'form': form})


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
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            check_in = form.cleaned_data['check_in']
            check_out = form.cleaned_data['checkout']
            if not space.is_available(check_in, check_out):
                # Space is not available for booking
                return render(request, 'base.html', {'space': space})
            # Create a new booking
            booking = form.save(commit=False)
            booking.space = space
            booking.client = request.user
            # Update space availability
            space.is_booked = True
            space.save()
            space.book(check_in, check_out)
            booking.save()
            # Redirect to the booking confirmation page
            return redirect('bookings')
    else:
        form = BookingForm()
        return render(request, 'book.html', {'space': space, 'form': form})


def create_space(location_obj, capacity):
    for i in range(capacity):
        space_name = f"{location_obj.name} Space {i+1}"
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

        print(booking.checkout.strftime('%Y-%m-%d %H:%M:%S') < datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        if booking.checkout.strftime('%Y-%m-%d %H:%M:%S') <= datetime.now().strftime('%Y-%m-%d %H:%M:%S'):
            booking.space.is_booked = False
            booking.space.save()