from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .models import Time
from .forms import RequestReservationForm
import jdatetime
from .utils import send_temporary, send_sms_to_admin
from datetime import date
from django.contrib import messages
from django.views.decorators.cache import never_cache


def home(request):
    return render(request, 'home/home_page.html')

@never_cache
@login_required
def calendar(request):
    if request.method == 'POST':
        form = RequestReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.save()

            phone = reservation.user.phone_number
            name = reservation.user.name
            miladi_date = form.cleaned_data['suggested_reservation_date']
            shamsi_date = jdatetime.date.fromgregorian(date=miladi_date)
            date = shamsi_date.strftime('%Y/%m/%d')

            send_temporary(phone, name, date)
            print('sms ok')

            User = get_user_model()
            admin_users = User.objects.filter(is_superuser=True)

            for admin in admin_users:
                miladi_date = form.cleaned_data['suggested_reservation_date']
                shamsi_date = jdatetime.date.fromgregorian(date=miladi_date)
                date_request = shamsi_date.strftime('%Y/%m/%d')

                phone_user = reservation.user.phone_number

                send_sms_to_admin(admin.phone_number, date_request, phone_user, name)

            return redirect('welcome')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
            return redirect('calendar')
    else:
        form = RequestReservationForm()

    return render(request, 'home/reservation.html', {'form': form})


@staff_member_required
def dashbord(request):
    today = date.today()
    today_reserve = Time.objects.filter(fix_reserved_date=today)
    upcoming = Time.objects.filter(fix_reserved_date__gt=today).order_by('fix_reserved_date')[:10]
    total = Time.objects.count()
    print("TODAY:", today)

    return render(request, 'home/dashbord.html', {

        'today_reserve': today_reserve,
        'upcoming': upcoming,
        'total': total,

    })


def contact_us(request):
    return render(request , 'home/contact_us.html')

def about_us(request):
    return render(request, 'home/about_us.html')

