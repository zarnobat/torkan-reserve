from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.http import JsonResponse
from django.core.paginator import Paginator
from home.models import Time, RequestReservation
from .forms import *
from .models import *
from random import randint
from .utils import send_code
from accounts.models import User
from django.views.decorators.cache import never_cache
from config.settings import DEBUG
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages


def phone_number_view(request):
    if request.method == 'POST':
        form = PhoneNumberForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            name = form.cleaned_data.get('name', '')

            token = str(randint(1000, 9999))
            request.session['phone_number'] = phone_number
            request.session['verification_code'] = token
            request.session['name'] = name
            # Just for don`t use SMS in development mode
            if not DEBUG:
                send_code(phone_number, token)
            print(f" $--------------------$ {token} $--------------------$ ")
            return redirect('code_view')
    else:
        form = PhoneNumberForm()

    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect("home")


@never_cache
def verify(request):
    if request.method == 'POST':
        form = VerificationCodeForm(request.POST)
        if form.is_valid():
            entered_code = form.cleaned_data['verification_code']
            stored_code = request.session.get('verification_code')
            phone_number = request.session.get('phone_number')
            name = request.session.get('name')

            if entered_code == stored_code:
                # پیدا کردن یا ساختن کاربر
                user, created = User.objects.get_or_create(
                    phone_number=phone_number)

                if created:
                    user.name = name
                    user.save()

                # احراز هویت و لاگین کردن کاربر
                user = authenticate(
                    request, phone_number=phone_number, verification_code=entered_code)
                if user is not None:
                    login(request, user)

                    # پاک کردن داده‌های سشن
                    request.session.pop('verification_code', None)
                    request.session.pop('phone_number', None)
                    request.session.pop('name', None)

                    # ریدایرکت هوشمند بر اساس نوع کاربر
                    if user.is_staff:
                        return redirect('employee_panel')
                    else:
                        return redirect('custom_panel')
                else:
                    form.add_error('verification_code', 'خطا در احراز هویت')
            else:
                form.add_error('verification_code', 'کد وارد شده اشتباه است')
    else:
        form = VerificationCodeForm()

    return render(request, 'registration/verify.html', {'form': form})


def welcome(request):
    return render(request, 'registration/welcome.html')


def custom_permission_denied_view(request, exception):
    return render(request, '403.html', status=403)


@login_required
def custom_panel(request):

    user = request.user
    profile = CustomerProfile.objects.filter(user=user).first()
    tickets = SupportTicket.objects.filter(sender=user).order_by('-created_at')
    reserves = Time.objects.filter(
        request_reservation__user=user).order_by('-fix_reserved_date')
    suggestions = RequestReservation.objects.filter(
        user=user).order_by('-suggested_reservation_date')
    invoices = Invoice.objects.filter(
        customer__user=user).order_by('created_date')

    success = False
    open_modal = False

    if request.method == 'POST':
        # Create ticket from modal
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.sender = request.user
            ticket.save()
            request.session['ticket_success'] = True
            return redirect('custom_panel')
        else:
            open_modal = True
    else:
        form = SupportTicketForm()

    if request.session.get('ticket_success'):
        success = True
        del request.session['ticket_success']

    context = {
        'profile': profile,
        'tickets': tickets,
        'reserves': reserves,
        'suggestions': suggestions,
        'invoices': invoices,
        'form': form,
        'success': success,
        'open_modal': open_modal,
    }

    return render(request, 'registration/custom_panel.html', context)


def ticket_success(request):
    return render(request, 'registration/ticket_success.html')


def custom_create_ticket(request, template_name='registration/customer_ticket.html'):
    success = False
    login_required_message = False

    if request.method == 'POST':
        if not request.user.is_authenticated:
            # Save message in session & redirect
            request.session['login_required_message'] = True
            return redirect(request.path)
        else:
            form = SupportTicketForm(request.POST)
            if form.is_valid():
                ticket = form.save(commit=False)
                ticket.sender = request.user
                ticket.save()
                request.session['ticket_success'] = True
                return redirect(request.path)
    else:
        # Ceck session messages
        if request.session.get('login_required_message'):
            login_required_message = True
            del request.session['login_required_message']

        if request.session.get('ticket_success'):
            success = True
            del request.session['ticket_success']

    form = SupportTicketForm()

    return render(request, template_name, {
        'form': form,
        'success': success,
        'login_required_message': login_required_message
    })


@staff_member_required
@login_required
def staff_create_ticket(request):
    success = False
    ticket_type = None
    
    if request.method == 'POST':

        if 'select_ticket_type' in request.POST:
            ticket_type = request.POST.get('ticket_type')
            form = EmployeeTicketForm(initial={
                                      'employee': request.user, 'ticket_type': ticket_type}, ticket_type=ticket_type)
        else:
            form = EmployeeTicketForm(request.POST)
            if form.is_valid():
                ticket = form.save(commit=False)
                ticket.employee = request.user
                ticket.save()
                return redirect('ticket_success')
            else:
                # Save form errors and data in session
                request.session['form_errors'] = form.errors
                request.session['form_data'] = request.POST
                return redirect('staff_ticket')
    else:
        # Check if there are form data in session
        if 'form_data' in request.session:
            form = EmployeeTicketForm(data=request.session['form_data'])
            form._errors = request.session.pop('form_errors', form.errors)
            request.session.pop('form_data', None)
        else:
            form = EmployeeTicketForm(initial={'employee': request.user})
    return render(request, 'registration/employee_ticket.html', {'form': form, 'ticket_type': ticket_type})



@login_required
def employee_panel(request):
    user = request.user
    profile = get_object_or_404(StaffProfile, user=user)
    workhours = WorkHourReport.objects.filter(
        employee=profile).order_by('month')
    payslips = Payslip.objects.filter(
        employee=profile).order_by('-date_created')
    tickets = EmployeeTicket.objects.filter(
        employee=user).select_related('employee').order_by('-created_at')
    context = {
        'profile': profile,
        'workhours': workhours,
        'payslips': payslips,
        'tickets': tickets,
    }

    return render(request, 'registration/employee_panel.html', context)


@login_required
def answer_custom(request):

    user = request.user

    tickets = (
        SupportTicket.objects
        .filter(sender=user)
        .prefetch_related('replies')
        .order_by('-created_at'))

    # print(answers)

    return render(request, 'registration/answer_custom.html', {'tickets': tickets})


@staff_member_required
@login_required
def answer_employee(request):
    user = request.user
    tickets = (
        EmployeeTicket.objects
        .filter(employee=user)
        .prefetch_related('replies')
        .order_by('-created_at')
    )

    return render(request, 'registration/answer_employee.html', {'tickets': tickets})


@login_required
def suggestion(request):
    success = False
    if request.method == 'POST':
        form = SuggestionForm(request.POST)
        if form.is_valid():
            suggestion = form.save(commit=False)
            suggestion.user = request.user
            suggestion.user_type = 'staff' if request.user.is_staff else 'customer'
            suggestion.save()
            success = True
            form = SuggestionForm()  # فرم جدید برای نمایش
    else:
        form = SuggestionForm()

    back_url = 'employee_panel' if request.user.is_staff else 'custom_panel'
    return render(request, 'registration/suggestion.html', {'form': form, 'success': success, 'back_url': back_url})


def employee_login(request):
    if request.method == 'POST':
        form = PhoneNumberForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            name = form.cleaned_data.get('name', '')

            token = str(randint(1000, 9999))
            request.session['phone_number'] = phone_number
            request.session['verification_code'] = token
            request.session['name'] = name
            # Just for don`t use SMS in development mode
            if not DEBUG:
                send_code(phone_number, token)
            print(f" $--------------------$ {token} $--------------------$ ")
            return redirect('code_view')
    else:
        form = PhoneNumberForm()
    return render(request ,'registration/employee_login.html',{'form': form})

@login_required
def staff_or_customer(request):
    user = request.user
    if user.is_staff:
        return redirect('employee_panel')   # باید name در urls.py باشه
    else:
        return redirect('custom_panel')
