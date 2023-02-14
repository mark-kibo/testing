from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
import datetime

#import our models for use
from .models import Spaces, Bookings

# Create your views here.

def index(request):
    update_time(Bookings, Spaces)
    if request.method == "POST":
        spaces=Spaces.objects.all()

        id_number=request.POST['id_no']
        plate_number=request.POST['plate']
        parking_location=request.POST['location']
       
        try:
            data=get_object_or_404(Spaces, parking_location = parking_location)
            if data.number_of_spaces > 0 :
                #store parameters passed temporarily
                request.session['param1'] = id_number
                request.session['param2'] = plate_number
                request.session['param3'] = parking_location
                return redirect('book')
            else:
                messages.info(request, "parking spaces full, please try another location")
                return render(request, 'index.html', {'spaces': spaces})

        except Exception as e:
            messages.info(request, "{}".format(e))
            return redirect('/')
    else:
        spaces=Spaces.objects.all()
        return render(request, 'index.html', {'spaces': spaces})


def pricing(request):
    spaces=Spaces.objects.all()
    print(spaces)
    return render(request, 'pricing.html', {'spaces': spaces})

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

@login_required(login_url="login_user")
def bookings(request):
    return render(request, 'bookings.html')


def login_user(request):
    if request.method == "POST":
        username=request.POST['name']
        password=request.POST['password']

        #authenticate our user
         
        user=authenticate(username=username, password=password)
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
        form=RegisterForm(request.POST)
        if form.is_valid():
            #get  form data
            name=form.cleaned_data['username']
            password=form.cleaned_data['password1']

            # dont commit changes to allow an update
            update_data=form.save(commit=False) 
            update_data.is_customer=True # set user to customer
            update_data.save()
            print(name)
            #authenticate user
            user=authenticate(username=name, password=password)
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
        form=RegisterForm()
    return render(request, 'register.html', {'form':form})

def parking_admin(request):
    return render(request, 'parking-admin/login.html')

def logout_user(request):
    logout(request)
    return redirect('home')


@login_required(login_url="login_user")
def book(request):
    #Access the parameters passed
    param1 = request.session.get('param1', None)#id number
    param2 = request.session.get('param2', None)# plate
    param3 = request.session.get('param3', None)# location
    space_number_available=get_object_or_404(Spaces, parking_location=param3)
    if request.method == "POST":
        #get form values
        check_in_date=request.POST['date_in']
        check_in_time=request.POST['check_in_time']
        check_out_date=request.POST['date_out']
        check_out_time=request.POST['check_out_time']
        mpesa_number=request.POST['mpesa_no']
        amount=request.POST['amount_paid']

        print(datetime.datetime.strptime(check_out_time, "%H:%M").time() < datetime.datetime.now().replace(second=0, microsecond=0).time())
        # check to see if user exists
        if Bookings.objects.filter(client=request.user).exists():
            if Bookings.objects.get(client=request.user).check_out_time < datetime.datetime.now().replace(second=0, microsecond=0).time():
                return HttpResponse("cant book till time is over")
            else:
                book = Bookings.objects.get(client=request.user)
                book.check_out_time=check_out_time 
                book.check_in_date=check_in_date 
                book.check_in_time=check_in_time 
                book.check_out_date=check_out_date 
                book.location=space_number_available
                space_number_available.number_of_spaces -= 1
                book.save()
                space_number_available.save()
                return HttpResponse("saved")
        else:
            new_instance=Bookings.objects.create(
                client=request.user,
                location = space_number_available,
                government_id=param1,
                car_plate = param2,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                check_in_time=check_in_time,
                check_out_time=check_out_time
            )
            new_instance.save()
        
            return HttpResponse('instace created')
    else:
        data=None
        try:
            #price of each locations
            data=get_object_or_404(Spaces, parking_location=param3)
        except:
            messages.info(request, "error")
        return render(request, "book.html", {'price': data.pricing_per_hour})



# function to update the spaces once a time allocated is over

def update_time(obj1, obj2):
    data=obj1.objects.all()
    if data:
        for x in data:
            if datetime.datetime.now().replace(second=0, microsecond=0).time() > x.check_out_time and  datetime.datetime.combine(datetime.datetime.today(), datetime.time.min).date() == x.check_out_date:
                    data2 = obj2.objects.get(parking_location = x.location)
                    data2.number_of_spaces += 1
                    data2.save()
            else:
                pass
    else:
        print("no bookings")