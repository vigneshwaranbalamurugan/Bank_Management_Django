
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login  as auth_login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from main.models import Customer,Transaction
from django.contrib.auth import logout
from django.contrib import messages
from decimal import Decimal
from django.views.decorators.cache import cache_control
from django.contrib.auth.hashers import check_password
from django.db import connection
from django.core.mail import send_mail
from django.conf import settings

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('home')
    else:
      error="Login Required"
      messages.error(request, error)
      return redirect('login')

@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def dashboard(request):
   if request.user.is_authenticated:
    user = request.user
    return render(request, 'home/dashboard.html', {'user': user})
   else:
     error="Login Required"
     messages.error(request, error)
     return redirect('login')
  

def home(request):
    return render(request, 'home/home.html')

def authenticat(username=None, password=None):
    try:
        print(username)
        user = Customer.objects.get(Customer_name=username)
        if user.password==password:
            return user
    except Customer.DoesNotExist:
        return None
    
def authenticatee(username=None, password=None):
    try:
        table_name = Customer._meta.db_table
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT id, password FROM {table_name} WHERE Customer_name = %s", [username])
            row = cursor.fetchone()
        
        if row is not None:
            user_id, db_password = row
            if password==db_password:
                user = Customer.objects.get(id=user_id)
                return user
    except Customer.DoesNotExist:
        return None

def login_view(request):
    error = None
    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticat(username=username, password=password)
        if user is not None:
            auth_login(request,user)
            messages.success(request, 'Login successfully!')
            request.session['user_id'] = user.id

            return redirect('dashboard')  
        else:
            error = 'Invalid username or password.'
    else:
        next_page = request.GET.get('next', '')
        return render(request, 'home/login.html', {'next': next_page})
    return render(request, 'home/login.html', {'error': error})

@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def update_user(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
    # Get form data
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            gender = request.POST.get('gender')
            phone_number = request.POST.get('phone_number')

            # Update user details
            user = request.user
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.gender = gender
            user.phone_number = phone_number
            user.email_customer = email  # Assuming `email_customer` is a separate field
            user.save()

            # Send success message
            messages.success(request, 'Your details have been updated successfully!')

            # Prepare email content with updated fields
            email_subject = 'Profile Updation Details'
            email_message = f"""
            Dear {first_name},

            Your profile has been updated successfully! Here are your updated details:

            First Name: {first_name}
            Last Name: {last_name}
            Email: {email}
            Gender: {gender}
            Phone Number: {phone_number}

            If you did not request these changes, please contact us immediately.

            Regards,
            TVK BANK
            """

            # Send email with updated details
            send_mail(
                email_subject,
                email_message,
                settings.EMAIL_HOST_USER,
                [email]
            )

            return redirect('dashboard')

    else:
     error="Login Required"
     messages.error(request, error)
     return redirect('login')

@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def create_transaction(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            sender_id = request.user.id
            receiver_id = request.POST.get('receiver_id')
            amount = Decimal(request.POST.get('amount'))

            sender = Customer.objects.get(id=sender_id)
            try:
                receiver = Customer.objects.get(id=receiver_id)
            except Customer.DoesNotExist:
                messages.error(request, 'Receiver not found.')
                return redirect('dashboard')  
            if sender.id==receiver.id:
                messages.error(request, 'Not possible to transfer for same account.')
                return redirect('dashboard')
            if receiver.id==1:
                messages.error(request, 'Not possible to transfer for this account.')
                return redirect('dashboard')
            if amount<100:
                messages.error(request, 'Minimum amount to transfer is 100.')
                return redirect('dashboard')       
            if sender.balance - amount >= 500:
                sender.balance -= amount
                sender.save()

                receiver.balance += amount
                receiver.save()

                transaction = Transaction.objects.create(
                    sender=sender,
                    receiver=receiver,
                    amount=amount
                )

                messages.success(request, f'Transaction completed successfully! {transaction}')
                send_mail('Transaction Details', f'Transaction completed successfully!\nAmount : {transaction.amount} from user {transaction.sender}.\nYour Current balance! {receiver.balance}.', settings.EMAIL_HOST_USER, [receiver.email_customer])
                send_mail('Transaction Details', f'Transaction completed successfully!\nAmount : {transaction.amount} to user {transaction.receiver}.\nYour Current balance! {sender.balance}', settings.EMAIL_HOST_USER, [sender.email_customer])
                return redirect('dashboard')  
            else:
                messages.error(request, 'Insufficient balance. Minimum balance of 500 must be maintained.')
                return redirect('dashboard')
    else:
        error="Login Required"
        messages.error(request, error)
        return redirect('login')

@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def trans_hist(request):
    if request.user.is_authenticated:
        user = request.user  
        sent_transactions = Transaction.objects.filter(sender=user)
        received_transactions = Transaction.objects.filter(receiver=user)
        
        transactions = sorted(
            list(sent_transactions) + list(received_transactions),
            key=lambda x: x.date,
            reverse=True
        )
        return render(request, 'home/dashboard.html', {'user': user,'transactions':transactions})
    else:
        error="Login Required"
        messages.error(request, error)
        return redirect('login')