from datetime import datetime
from django.contrib import messages

# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import User, Bus,Book,City
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import UserLoginForm, UserRegisterForm
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse




def home(request):
        return render(request, 'myapp/home.html')


def findbus(request):
    context = {}

    cities = City.objects.all()  # Fetch all cities from the database

    context['cities'] = cities  # Pass the cities data to the template

    if request.method == 'POST':
        source_r = request.POST.get('source')
        dest_r = request.POST.get('destination')
        date_r = request.POST.get('date')
        date_r = datetime.strptime(date_r, "%Y-%m-%d").date()
        year = date_r.strftime("%Y")
        month = date_r.strftime("%m")
        day = date_r.strftime("%d")
        bus_list = Bus.objects.filter(source=source_r, dest=dest_r, date__year=year, date__month=month, date__day=day)
        if bus_list:
            return render(request, 'myapp/list.html', {'bus_list': bus_list})
        else:
            context['data'] = request.POST
            context["error"] = "No available Bus Schedule for the entered Route and Date"
            return render(request, 'myapp/findbus.html', context)
    else:
        return render(request, 'myapp/findbus.html', context)
    



@login_required(login_url='signin')
def bookings(request):
    context = {}
    if request.method == 'POST':
        id_r = request.POST.get('bus_id')
        seats_r = int(request.POST.get('no_seats'))
        bus = Bus.objects.get(id=id_r)
        if bus:
            if bus.rem >= seats_r:
                name_r = bus.bus_name
                cost = seats_r * bus.price
                source_r = bus.source
                dest_r = bus.dest
                nos_r = Decimal(bus.nos)
                price_r = bus.price
                date_r = bus.date
                time_r = bus.time
                username_r = request.user.username
                email_r = request.user.email
                userid_r = request.user.id
                rem_r = bus.rem - seats_r
                Bus.objects.filter(id=id_r).update(rem=rem_r)
                book = Book.objects.create(name=username_r, email=email_r, userid=userid_r, bus_name=name_r,
                                           source=source_r, busid=id_r,
                                           dest=dest_r, price=price_r, nos=seats_r, date=date_r, time=time_r,
                                           status='BOOKED')

                # Send booking confirmation email to the user's email address
                subject = "Booking Confirmation"
                message = f"""
                Your booking details:
                Bus name: {name_r}
                Starting point: {source_r}
                Destination point: {dest_r}
                Number of seats: {seats_r}
                Price: {price_r}
                Cost: {cost}
                Date: {date_r}
                Time: {time_r}
                

                Thanks and Regards
                SRM Corporation services
                Neerukonda,Mangalagiri Mandal
                Andhra Pradesh
                522502
                """
                
                # Send the email using Django's send_mail function
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email_r],
                    fail_silently=False,
                )

                # Pass the booking details to the template for displaying the confirmation
                return render(request, 'myapp/bookings.html', locals())

            else:
                context["error"] = "Sorry, select fewer number of seats."
                return render(request, 'myapp/findbus.html', context)
        else:
            context["error"] = "Sorry, the selected bus does not exist."
            return render(request, 'myapp/findbus.html', context)

    else:
        return render(request, 'myapp/findbus.html')



@login_required(login_url='signin')
def cancellings(request):
    context = {}
    if request.method == 'POST':
        id_r = request.POST.get('bus_id')
        #seats_r = int(request.POST.get('no_seats'))

        try:
            book = Book.objects.get(id=id_r)
            bus = Bus.objects.get(id=book.busid)
            rem_r = bus.rem + book.nos
            Bus.objects.filter(id=book.busid).update(rem=rem_r)
            #nos_r = book.nos - seats_r
            Book.objects.filter(id=id_r).update(status='CANCELLED')
            Book.objects.filter(id=id_r).update(nos=0)
            messages.success(request, "Booked Bus has been cancelled successfully.")
            return redirect(seebookings)
        except Book.DoesNotExist:
            context["error"] = "Sorry You have not booked that bus"
            return render(request, 'myapp/error.html', context)
    else:
        return render(request, 'myapp/findbus.html')


@login_required(login_url='signin')
def seebookings(request):
    id_r = request.user.id
    book_list = Book.objects.filter(userid=id_r)

    if book_list.exists():
        context = {
            'book_list': book_list,
        }
        return render(request, 'myapp/booklist.html', context)
    else:
        context = {
            'error': "Sorry, no buses booked.",
        }
        return render(request, 'myapp/findbus.html', context)


def signup(request):
    context = {}
    if request.method == 'POST':
        name_r = request.POST.get('name')
        email_r = request.POST.get('email')
        password_r = request.POST.get('password')

        # Check if the username already exists
        if User.objects.filter(username=name_r).exists():
            context["error"] = "This username has already been taken. Please choose a different username."
            return render(request, 'myapp/signup.html', context)

        try:
            user = User.objects.create_user(username=name_r, email=email_r, password=password_r)
            login(request, user)
            return render(request, 'myapp/thank.html')
        except Exception as e:
            context["error"] = "Unable to create the account. Please try again."
            return render(request, 'myapp/signup.html', context)
    else:
        return render(request, 'myapp/signup.html', context)


def signin(request):
    context = {}
    if request.method == 'POST':
        name_r = request.POST.get('name')
        password_r = request.POST.get('password')
        user = authenticate(request, username=name_r, password=password_r)
        if user:
            login(request, user)
            if user.is_staff:
                # Admin user, redirect to admin:index
                return redirect('admin:index')
            else:
                # Regular user, redirect to findbus
                return redirect('success')
        else:
            context["error"] = "Provide valid credentials"
            return render(request, 'myapp/signin.html', context)
    else:
        context["error"] = "You are not logged in"
        return render(request, 'myapp/signin.html', context)



def signout(request):
    context = {}
    logout(request)
    context['error'] = "You have been logged out"
    return render(request, 'myapp/signin.html', context)


def success(request):
    context = {}
    context['user'] = request.user
    return render(request, 'myapp/success.html', context)


def searchbus(request):
    context = {}

    cities = City.objects.all()  

    context['cities'] = cities  

    if request.method == 'POST':
        source_r = request.POST.get('source')
        dest_r = request.POST.get('destination')
        date_r = request.POST.get('date')
        date_r = datetime.strptime(date_r, "%Y-%m-%d").date()
        year = date_r.strftime("%Y")
        month = date_r.strftime("%m")
        day = date_r.strftime("%d")
        bus_list = Bus.objects.filter(source=source_r, dest=dest_r, date__year=year, date__month=month, date__day=day)
        if bus_list:
            return render(request, 'myapp/list.html', {'bus_list': bus_list})
        else:
            context['data'] = request.POST
            context["error"] = "No available Bus Schedule for the entered Route and Date"
            return render(request, 'myapp/findbus.html', context)
    else:
        return render(request, 'myapp/findbus.html', context)
    

def safety(request):
    return render(request,'myapp/safety.html')
