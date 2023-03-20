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

from requests.api import request
import requests
import datetime as dt
import base64
from requests.auth import HTTPBasicAuth
# import our models for use
from .models import Location, ParkingSpace, Booking, ReserveUser, Address, Payout

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
        print(user.is_customer)
        if user is not None:
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
        # Redirect to the booking confirmation page
        return redirect('bookings')
    
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
    data.save()    
    update_space_availability()
    return redirect('payout', pk)
   

def payout(request, pk):
    if request.method == "POST":
        #mpesa code for stkpush
        timestamp=dt.datetime.now().strftime("%Y%m%d%H%M%S")#get timestamp in fom of string

        #get password
        data_to_encode=mpesa_express_shortcode +mpesa_passkey+ timestamp
        encoded=base64.b64encode(data_to_encode.encode())
        decoded_password=encoded.decode('utf-8')

        #auth credentials ur to get an access token
        auth_url ="https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

        r=requests.get(auth_url, auth=HTTPBasicAuth(mpesa_consumer_key,mpesa_consumer_secret))

        access_token=r.json()['access_token']

        #stk push url
        api_url="https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers={
            "Authorization":"Bearer %s" % access_token
        }

        # get data from phone
        phone_number=request.POST['phone']
        amount=request.POST['amount']

        request_mpesa={
            "BusinessShortCode":mpesa_express_shortcode,    
            "Password": decoded_password,    
            "Timestamp":timestamp,    
            "TransactionType": "CustomerPayBillOnline",    
            "Amount":1,    
            "PartyA":f"{phone_number}",    
            "PartyB":mpesa_express_shortcode,    
            "PhoneNumber":f"{phone_number}",    
            "CallBackURL":"https://darajambili.herokuapp.com/express-payment",    
            "AccountReference":"RESERVESPACE",    
            "TransactionDesc":"Car parking payment"
        }
    
        response=requests.post(api_url, json=request_mpesa, headers=headers)
        if response:
            booking=get_object_or_404(Booking, id=pk)
            request.session['param5']=pk
            if Payout.objects.filter(booking_id=booking).exists():
                return redirect('payments')
            else:
                payment=Payout.objects.create(
                    booking_id =booking ,payment_amount=amount,  payment_status="paid" , payment_method="mpesa" 
                )
                payment.save()
                return redirect('payout', pk)
        else:
            return redirect('bookings')
    else:
        book_obj=get_object_or_404(Booking, id=pk)
        price_per_hour = book_obj.space.location.pricing_per_hour
        time_spent=request.session.get('param4')
        total_amount=price_per_hour * time_spent
        return render(request, "payout.html", {'amount': total_amount})

def payments(request):
    try:
        book_obj=get_object_or_404(Booking, id=request.session.get('param5'))
        pay_obj=Payout.objects.filter(booking_id=book_obj)
    except:
        pay_obj={}
    return render(request, "book.html", {'pay_obj':pay_obj})


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

def delete_booking(request, pk):
    Book_obj=get_object_or_404(Booking, id=pk)
    Book_obj.delete()
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


def  maps(request):
    data=Address.objects.all()
    print(type(data))
    return render(request, "map.html", {'data': data})


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