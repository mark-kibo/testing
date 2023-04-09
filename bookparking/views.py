from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, BookingForm
from django.utils import timezone
from datetime import datetime, timedelta
import pytz
from datetime import date
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from django.http import JsonResponse
import json
import uuid

from django.conf import settings
from django.core.mail import send_mail 

from requests.api import request
import requests
import datetime as dt
import base64
from requests.auth import HTTPBasicAuth
# import our models for use
from .models import Location, ParkingSpace, Booking, ReserveUser, Payout
from .forms import UpdatepaymentForm
from .mpesa import mpesa_stk


#mpesa needed stuff
mpesa_environment="sandbox"
mpesa_consumer_key="O2eBlmzo47MnRZlMGqGKqwn2YqssPfnU"
mpesa_consumer_secret="VRjiW4fZSCJsdFPd"
lnm_phone_number='254769347882'
mpesa_passkey='bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
mpesa_express_shortcode="174379"

# Create your views here.

#get  hidden parameters

def billing_receipt(request, pk):
    obj = get_object_or_404(Payout, id=pk)
    

    # Get data for receipt
    Transaction_id = f"{obj.transaction_id}"
    """start_date = obj.check_in.strftime('%Y-%m-%d %H:%M:%S').split(" ")[0]
    end_date = obj.checkout.strftime('%Y-%m-%d %H:%M:%S').split(" ")[0]
    start_time = obj.check_in.strftime('%Y-%m-%d %H:%M:%S').split(" ")[1][:-3]
    end_time = obj.checkout.strftime('%Y-%m-%d %H:%M:%S').split(" ")[1][:-3]"""
    payment_date= obj.payment_date.strftime('%Y-%m-%d %H:%M:%S').split(" ")[0]
    amount = obj.payment_amount
    location=obj.space.location.name
    space=obj.space.name


    # Set colors
    blue_color = "#0066CC"
    dark_gray_color = "#333333"
    light_gray_color = "#CCCCCC"

     # Create data for table
    data = [
        
        ["Transaction_id", "Location", "space name", "Paid amount",  "payment date"],
        [Transaction_id, location,space,  f"${amount:.2f}"], payment_date]

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
    update_space_availability()
    if request.method == "POST":
        try:
            id_number = request.POST['id_no']
            plate_number = request.POST['plate']
            parking_location = request.POST['location']
            space=request.POST['spaces']
            checkin=request.POST['checkin']
            print(space)

            request.session['param1']=id_number
            request.session['param2']=plate_number
            request.session['param3']=checkin
            return redirect('book', space)
        except Exception as e:
            messages.info(request, "There are no available spaces on the specified location")
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
     
        if user is not None:
            if user.is_customer:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, "incorrect username or password")
                return redirect('login_user')
        else:
            messages.info(request, "user does not exist")
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
            if user is not None:
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
    location = get_object_or_404(Location, name=parking_location)

    spaces = ParkingSpace.objects.filter(location=location, is_booked=False)
    return render(request, "base.html", {'location': location, 'spaces': spaces})


def book(request, space_id):
    space = get_object_or_404(ParkingSpace, id=space_id)
    client=get_object_or_404(ReserveUser, username=request.user.username)
    today = datetime.today()
    books= Booking.objects.filter(has_expired=False, check_in__date=today, client=client).first()
    if books:
        messages.info(request, "you have an active booking")
        return redirect('bookings')
    else:
        request.session['space_id']=space_id
        booking=Booking.objects.create(
            check_in=request.session.get('param3'),
            space = space,
            client = request.user,
            government_id=request.session.get('param1'),
            car_plate=request.session.get('param2')    
        )
        booking.save()   
        space.is_booked=True
        space.save()
        messages.info(request, "book confirmed")
        return redirect('bookings')
        # Redirect to the booking confirmation page
        
    
def end_book(request, pk):
    nairobi_tz = pytz.timezone('Africa/Nairobi')
    now = datetime.now(nairobi_tz)
    data=Booking.objects.get(id=pk)
    timedelta = now - data.check_in
    request.session['param4']=timedelta.total_seconds() / 3600
    print(timedelta.total_seconds())
    """if timedelta.total_seconds() < 3600:
        data.checkout=now
        data.has_expired=True
        data.save()    
        update_space_availability()
        return redirect('payout', pk)
    else:
        messages.info(request, "The time difference is less than or equal to one hour")
        return redirect('bookings')"""
    data.checkout=now
    data.has_expired=True
    space=get_object_or_404(ParkingSpace, id=request.session.get('space_id'))
    space.is_booked=False
    space.save()
    data.save()    
    return redirect('payout', pk)
   

def payout(request, pk):
    if request.method == "POST":
        # get data from phone
        phone_number=request.POST['phone']
        amount=request.POST['amount']
        email=request.POST['email']

        response=mpesa_stk(amount, phone_number,mpesa_express_shortcode , mpesa_passkey, mpesa_consumer_key, mpesa_consumer_secret)
        print(response.text)
       
        payment_status = "not paid" if not response else "paid"

        booking=get_object_or_404(Booking, id=pk)
        client = ReserveUser.objects.get(username=request.user)
        request.session['param5']=pk
        payment, created = Payout.objects.get_or_create(
               space=booking.space , client=client, payment_method="mpesa",
               defaults={
                   'transaction_id': uuid.uuid4(),
                   'payment_amount': amount,
                   'payment_status': payment_status
               }
        )

        if not created:
            payment.payment_amount = amount
            payment.payment_status = payment_status
            payment.save()

        if payment_status == "paid":
            return redirect('payments')
        else:
            return redirect('payout', pk)
    else:
        book_obj=get_object_or_404(Booking, id=pk)
        price_per_hour = book_obj.space.location.pricing_per_hour
        time_spent=request.session.get('param4')
        client = ReserveUser.objects.get(username=request.user)
        total_amount=price_per_hour * time_spent
        payment, created = Payout.objects.get_or_create(
               space=book_obj.space , client=client, payment_method="mpesa",
               defaults={
                   'transaction_id': uuid.uuid4(),
                   'payment_amount': 0,
                   'payment_status': "not paid"
               }
        )

        if not created:
            payment.payment_amount = 0
            payment.payment_status = "not paid"
            payment.save()

        return render(request, "payout.html", {'amount': total_amount})




def payments(request):
    try:
        today = timezone.now().date()
        client = ReserveUser.objects.get(username=request.user)
        pay_obj=Payout.objects.filter(client=client, payment_date__date=today).all()
        print(pay_obj)
    except:
        pay_obj={}
    return render(request, "payments.html", {'pay_obj':pay_obj, 'booking_id': request.session.get('param5')})


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
            print(f"done")

def delete_booking(request, pk, sp):
    Book_obj=get_object_or_404(Booking, id=pk)
    Book_obj.delete()
    space=get_object_or_404(ParkingSpace, id=sp)
    space.is_booked=False
    space.save()
    messages.info(request, f"{Book_obj.space} booking has been  deleted")
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


@login_required(login_url="login_user")
def maps(request, pk):
    location=get_object_or_404(Booking, id=pk)
    return render(request, "map.html", {"location":location.space.location.name})


def my_django_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        my_field_value = data.get('my_data')
        print(my_field_value)
        location = get_object_or_404(Location, name=my_field_value)
        print(location)
        spaces = ParkingSpace.objects.filter(location=location, is_booked=False)
        results = [{'id': obj.id, 'name': obj.name} for obj in spaces]
        # Process the data as needed
        return JsonResponse({'next_value': results})
    else:
        return JsonResponse({'error': 'Invalid request method'})




def mpesa_callback(request):
    return HttpResponse(request)



    


def update_payment(request, pk):
    payment=get_object_or_404(Payout, id=pk)

    if request.method == "POST":
        form=UpdatepaymentForm(request.POST, instance=payment)
        if form.is_valid():
            phone_number=request.POST['phone']
            amount=request.POST['amount']
            
            response=mpesa_stk(amount, phone_number,mpesa_express_shortcode , mpesa_passkey, mpesa_consumer_key, mpesa_consumer_secret)
            if response:
                payment = form.save(commit=False)
                payment.payment_amount = amount
                payment.payment_status = "paid"
                payment.save()
                messages.info(request, "paid, generate ticket")
                return redirect('payments')
            else:
                messages.info(request, "request failed try again")
                return redirect('payments')
    else:
        form=UpdatepaymentForm(instance=payment)
        return render(request, 'updatepayment.html', {'form':form})


