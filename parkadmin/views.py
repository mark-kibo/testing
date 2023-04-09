from django.shortcuts import render, redirect
import io
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from bookparking.models import ReserveUser, Booking, Location, ParkingSpace
from django.contrib import messages
from datetime import datetime
from django.template.loader import get_template
from xhtml2pdf import pisa

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from bookparking.forms import UserForm, RegisterForm, BookingForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required 
# Create your views here.

@login_required(login_url="login_employee")
def index(request):
    if request.user.is_employee:
        booking=Booking.objects.count()
        parking=Location.objects.count()
        parking_location=Location.objects.all()

        context={
            'booking':booking,
            'parking':parking,
            'parkings':parking_location
        }
        return render(request, "parking-admin/index.html", context)
    else:
        return redirect("login_employee")


def user_management(request):
    users = ReserveUser.objects.all()
    print(users)
    context = {'users': users}
    return render(request, "parking-admin/register.html", context)

def parkingspace_management(request):
    spaces = ParkingSpace.objects.all()
    print(spaces)
    context = {'spaces': spaces}
    return render(request, "parking-admin/update_spaces.html", context)

def booking_management(request):
    books= Booking.objects.all()
    print(books)
    context = {'books': books}
    return render(request, "parking-admin/bookings.html", context)


def parking_management(request):
    locations= Location.objects.all()
    context = {'locations': locations}
    return render(request, "parking-admin/pages-blank.html", context)

def reports(request):
    if request.method == 'POST':
        report_type = request.POST.get('reporttype')
        start_date_str = request.POST.get('startdate')
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date_str = request.POST.get('enddate')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        # Query the database based on report type and date range
        if report_type == 'daily':
            bookings = Booking.objects.filter(check_in__date=start_date.date())
        elif report_type == 'weekly':
            bookings = Booking.objects.filter(check_in__range=[start_date, end_date])
        elif report_type == 'monthly':
            bookings = Booking.objects.filter(check_in__month=start_date.month)

        print(start_date.date())
        print(bookings)

            
        context = {
            'bookings': bookings,
            'title': f'Parking Reports of {start_date_str} -{end_date_str}'
        }

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'filename="parking_report_{start_date_str}.pdf"'

        template_path = 'reporttable.html'

        template = get_template(template_path)
        html = template.render(context)
        print(template)

        # create a pdf
        pisa_status = pisa.CreatePDF(html, dest=response)

        # if error then show some funy view
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    return render(request, "parking-admin/table-basic.html")






def edit_user(request, user_id):
    user = get_object_or_404(ReserveUser, id=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        print(form)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully!')
            return HttpResponseRedirect(reverse('user'))
        else:
            messages.error(request, 'Please correct the errors below.')
            return HttpResponseRedirect(reverse('user'))
    else:
        form = UserForm(instance=user)
    context = {'form': form, 'user': user}
    return render(request, 'parking-admin/map-google.html', context)


@login_required
def delete_user(request, user_id):
    user = get_object_or_404(ReserveUser, id=user_id)
    user.delete()
    messages.success(request, 'User deleted successfully!')
    return HttpResponseRedirect(reverse('user'))


def add_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully!')
            return HttpResponseRedirect(reverse('user'))
        else:
            messages.error(request, 'Please correct the errors below.')
            return HttpResponseRedirect(reverse('user'))
    else:
        form = RegisterForm()
    context = {'form': form}
    return render(request, 'parking-admin/adduser.html', context)



def add_spaces(request):
    
    if request.method == "POST":
        location = request.POST['location']
        location_obj=Location.objects.get(name=location)
        capacity = request.POST['capacity']
        for i in range(int(capacity)):
            space_name = f"{location_obj.name.split(' ')[0]} {i+1}"
            space = ParkingSpace(location=location_obj,
                                name=space_name, is_booked=False)
            space.save()
        messages.info(request, f"spaces {capacity} have been created successfully")
        return HttpResponseRedirect(reverse('parkingspace_management'))
    else:
        locations=Location.objects.all()
        context={
            'locations':locations
        }
        return render(request, 'parking-admin/addspaces.html', context)



def edit_space(request, space_id):
    space = get_object_or_404(ParkingSpace, id=space_id)
    locations=Location.objects.all()
    if request.method == 'POST':
        location = request.POST['location']
        name = request.POST['name']
        location_obj=Location.objects.get(name=location)
        capacity = request.POST['capacity']
        booked=request.POST.get('booked')
        if booked:
            if space.is_booked == True:
                pass
            else:
                space.is_booked = True
        else:
            if space.is_booked == True:
                space.is_booked = False
        print(booked)
        space.location =location_obj
        space.name=name
        space.capacity=capacity
        space.save()
        messages.info(request, f"space {space_id} is updated succesfully ")
        return HttpResponseRedirect(reverse('parkingspace_management'))
    else:
        context = {'locations': locations, 'space': space}
        return render(request, 'parking-admin/updatespace.html', context)




def delete_space(request, space_id):
    space = get_object_or_404(ParkingSpace, id=space_id)
    space.delete()
    messages.info(request, f"space {space_id} is deleted succesfully ")
    return HttpResponseRedirect(reverse("parkingspace_management"))




def delete_book(request, pk):
    Book_obj=get_object_or_404(Booking, id=pk)
    Book_obj.delete()
    return HttpResponseRedirect(reverse('booking_management'))




def update_book(request, pk):
    obj=get_object_or_404(Booking, id=pk)
    if request.method == "POST":
        form = BookingForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.info(request, f'{obj} updated')
            return HttpResponseRedirect(reverse('booking_management'))
    else:
        form = BookingForm(instance=obj)
        return render(request, "parking-admin/book.html", {'form':form})
    

def add_reservation(request):
    users=ReserveUser.objects.all()
    locations=Location.objects.all()
    spaces=ParkingSpace.objects.filter(is_booked=False).all()
    
    if request.method == "POST":
        location=request.POST['location']
        space=request.POST['space']
        client=request.POST['user']
        checkinstr=request.POST['checkin']
        checkoutstr=request.POST['checkout']
        id=request.POST['id_number']
        plate=request.POST['plate']

        checkin=datetime.fromisoformat(checkinstr)
        checkout=datetime.fromisoformat(checkoutstr)


        space1 = get_object_or_404(ParkingSpace, id=space)
        user= get_object_or_404(ReserveUser, username=client)
        today = datetime.today()
        books= Booking.objects.filter(has_expired=False, checkout__date=today, client=user).first()
        print(books)

        if not space1.is_available(checkin, checkout):
            pass
        # Create a new booking
        if books:
            messages.info(request, "you have an active booking")
            return redirect('booking_management')
        else:
            booking = Booking.objects.create(space = space1,client = user, check_in=checkin, 
                                              checkout=checkout, government_id=id, car_plate=plate)
            # Update space availability
            space1.is_booked = True
            space1.save()
            space1.book(checkin, checkout)
            booking.save()
            messages.info(request, "book confirmed")

        return HttpResponseRedirect(reverse('booking_management'))
  
    else:
        context={
                'users':users,
                'locations':locations,
                'spaces':spaces
        }

        return render(request, "parking-admin/addreservation.html", context)
    

def add_parking(request):
    if request.method == "POST":
        name=request.POST['parking_name']
        capacity=request.POST['capacity']
        pricing=request.POST['pricing']
        image_location=request.FILES['location']

        if Location.objects.filter(name=name).exists():
            messages.info(request, "Parking location exists ")
            return HttpResponseRedirect(reverse('parking_management'))
        else:
            obj=Location.objects.create(name=name, capacity=capacity, pricing_per_hour=pricing, name_image=image_location)
            obj.save()
            messages.info(request, f"Parking location {name} added successfully")
            return HttpResponseRedirect(reverse('parking_management'))
    else:
        return render(request, "parking-admin/addparkinglocation.html")
    

def edit_parking(request, parking_id):
    parking=Location.objects.filter(id=parking_id).first()
    if request.method == "POST":
            name=request.POST.get('parking_name')
            capacity=request.POST.get('capacity')
            pricing=request.POST.get('pricing')
            image_location=request.FILES.get('location')

            obj= Location.objects.get(id=parking_id)
            if obj:
                obj.name=name
                obj.capacity=capacity
                obj.pricing_per_hour=pricing
                obj.name_image=image_location

                obj.save()
            messages.info(request, f"Parking location {name} added successfully")
            return HttpResponseRedirect(reverse(parking_management))
    else:
        print(parking.pricing_per_hour)
        return render(request, "parking-admin/editparking.html", {"parking": parking})

def delete_parking(request, parking_id):
    parking=Location.objects.filter(id=parking_id).first()
    parking.delete()
    messages.info(request, f"{parking} location deleted")
    return HttpResponseRedirect(reverse(parking_management))

def login_admin(request):
    if request.method == "POST":
        username = request.POST['name']
        password = request.POST['password']

        # authenticate our user

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_employee:
                login(request, user)
                return redirect('index')
            else:
                messages.info(request, "incorrect username or password")
                return redirect('login_employee')
    return render(request, 'parking-admin/login.html')


def logout_admin(request):
    logout(request)
    return redirect('login_employee')

def change_permission(request, id,  pk):
    if pk == "parkuser":
        user=get_object_or_404(ReserveUser, id=id)
        user.is_customer=True
        user.is_employee=False
        user.save()
        print("user is user")
        return redirect('user')
    else:
        user=get_object_or_404(ReserveUser, id=id)
        user.is_customer=False
        user.is_employee=True
        user.save()
        return redirect('user')