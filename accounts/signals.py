from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import CustomerProfile, StaffProfile, EmployeeTicketReply, EmployeeTicket, SupportTicket, TicketReply, Invoice, Payslip
from .utils import customer_ticket, employee_ticket, answer_customer, answer_employee, invoice_customer, payslip_employee, welcome_sms
import jdatetime
from home.models import Time
from home.utils import send_reservation_sms
from config.settings import DEBUG

User = get_user_model()


@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    if created:
        CustomerProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_staff_profile(sender, instance, created, **kwargs):

    if created and instance.is_staff:
        StaffProfile.objects.create(user=instance)
    else:

        if instance.is_staff and not hasattr(instance, 'staffprofile'):
            StaffProfile.objects.create(user=instance)

        elif not instance.is_staff and hasattr(instance, 'staffprofile'):
            instance.staffprofile.delete()


@receiver(post_save, sender=EmployeeTicketReply)
def update_ticket_status(sender, instance, created, **kwargs):
    if created and instance.author.is_staff:
        instance.ticket.status = 'answered'
        instance.ticket.save()


@receiver(post_save, sender=SupportTicket)
def cuetomer_ticket_sms(sender, instance, created, **kwargs):
    if created:
        # تبدیل به شمسی
        created_at_shamsi = jdatetime.datetime.fromgregorian(
            datetime=instance.created_at
        ).strftime("%Y/%m/%d")

        customer_ticket(
            instance.sender.name,
            created_at_shamsi,
            instance.sender.phone_number,
        )


@receiver(post_save, sender=EmployeeTicket)
def employee_ticket_sms(sender, instance, created, **kwargs):
    if created:

        employee_ticket(
            instance.employee.name,
            instance.get_ticket_type_display(),
            instance.employee.phone_number,
        )


@receiver(post_save, sender=TicketReply)
def answer_ticket_customer_sms(sender, instance, created, **kwargs):
    if created:
        created_at_shamsi = jdatetime.datetime.fromgregorian(
            datetime=instance.created_at
        ).strftime("%Y/%m/%d")

        answer_customer(
            instance.ticket.sender.name,
            created_at_shamsi,
            instance.ticket.sender.phone_number,
        )


@receiver(post_save, sender=EmployeeTicketReply)
def answer_ticket_employee_sms(sender, instance, created, **kwargs):
    if created:
        created_at_shamsi = jdatetime.datetime.fromgregorian(
            datetime=instance.created_at
        ).strftime("%Y/%m/%d")

        answer_employee(
            instance.ticket.employee.name,
            created_at_shamsi,
            instance.ticket.get_ticket_type_display(),
            instance.get_status_ticket_display(),
            instance.ticket.employee.phone_number,
        )


@receiver(post_save, sender=Invoice)
def answer_ticket_customer_sms(sender, instance, created, **kwargs):
    if created:
        created_at_shamsi = jdatetime.datetime.fromgregorian(
            datetime=instance.created_date
        ).strftime("%Y/%m/%d")

        invoice_customer(
            instance.customer.user.name,
            created_at_shamsi,
            instance.customer.user.phone_number,
        )


@receiver(post_save, sender=Payslip)
def payslip_employee_sms(sender, instance: Payslip, created, **kwargs):
    created_at_shamsi = jdatetime.datetime.fromgregorian(
        datetime=instance.date_created
    ).strftime("%Y/%m/%d")
    employee = instance.employee.user.name
    phone_number = instance.employee.user.phone_number

    if created and not DEBUG:
        payslip_employee(
            employee,
            created_at_shamsi,
            phone_number
        )
    elif created:
        print(f"------------------------------------------------------------------------\n\
                |                  payslip for {employee} - {phone_number}               |\n\
                ------------------------------------------------------------------------\n")

@receiver(post_save, sender=Time)
def sms_fixed_reseve(sender, instance, created, **kwargs):
    if created:
        created_at_shamsi = jdatetime.datetime.fromgregorian(
            datetime=instance.fix_reserved_date
        ).strftime("%Y/%m/%d")

        send_reservation_sms(
            instance.request_reservation.user.phone_number,
            instance.request_reservation.user.name,
            created_at_shamsi,
        )
    if created:
        print("$---- send fixed reservation time ----$\n")
    else:
        print("$---- Not send fixed reservation time ----$\n")


@receiver(post_save, sender=User)
def welcome(sender, instance, created, **kwargs):
    if created:
        date_joined = jdatetime.datetime.fromgregorian(
            datetime=instance.date_joined
        ).strftime("%Y/%m/%d")

        welcome_sms(
            instance.name,
            date_joined,
            instance.phone_number,
        )
