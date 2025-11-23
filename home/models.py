from django.db import models
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel


def default_reservation_date():
    return now().date()


class HomePage(Page):
    body = RichTextField(blank=True, verbose_name="محتوای صفحه اصلی")

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]


class Operation(models.Model):
    operation_name = models.CharField(max_length=50, verbose_name=_('Operation name'))

    def __str__(self):
        return self.operation_name

    class Meta:
        verbose_name = _("Operations")


class OperationSetting(models.Model):
    Unit = [
        ("gal", "گالن"),
        ("but", "بوته",),
        ("kilo", "کیلو گرم")
    ]

    operation = models.ForeignKey(Operation, on_delete=models.CASCADE, verbose_name=_('Operation type'), null=True,
                                  blank=True)
    unit_capacity = models.CharField(choices=Unit, max_length=10, null=True, blank=True,
                                     verbose_name=_('Unit of calculation'))
    capacity = models.IntegerField(default=0, verbose_name=_('Number of furnaces'))
    capacity_materials = models.IntegerField(default=1, verbose_name=_('Material volume'))
    zamini = models.BooleanField(verbose_name=_('Is there ground melting?'), default=False)
    Product = models.CharField(max_length=20, null=True, blank=True, verbose_name=_('Product name'))

    def calculation(self):
        Cap = 0
        Finaltime = 0
        kilo = 0

        if self.unit_capacity == 'but':
            galen = self.capacity_materials * 2
            kilo = galen * 17

            while kilo > 0:
                Cap += 1
                kilo -= 150

            Finaltime = Cap * 2


        elif self.unit_capacity == 'gal':
            galen = self.capacity_materials
            kilo = galen * 17

            while kilo > 0:
                Cap += 1
                kilo -= 150

            Finaltime = Cap * 2


        else:
            kilo = self.capacity_materials
            while kilo > 0:
                Cap += 1
                kilo -= 150

            Finaltime = Cap * 2

        return f"مدت زمان ذوب این مواد {Finaltime} ساعت میباشد"

    def display_calculation(self):
        return self.calculation()

    display_calculation.short_description = _('Melting time')

    class Meta:
        verbose_name = _('Approximate time')


class RequestReservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name=_('User'), )
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date created'))
    suggested_reservation_date = models.DateField(default=default_reservation_date, verbose_name=_('reservation date'))
    suggested_reservation_time = models.TimeField(default='08:00', null=True, blank=True,
                                                  verbose_name=_('suggested reservation time'))
    explanation = models.TextField(null=True, blank=True, verbose_name=_('Explanation'))
    status = models.CharField(choices=STATUS_CHOICES, max_length=10, default='pending', verbose_name=_('Status'))

    def __str__(self):
        return f"{self.id}) {self.user if self.user else '---'}"

    class Meta:
        verbose_name = _("Reservation requests")


class Time(models.Model):
    Unit = [
        ("gal", "گالن"),
        ("but", "بوته",),
        ("kilo", "کیلو گرم"),
    ]

    request_reservation = models.OneToOneField(RequestReservation, on_delete=models.CASCADE,blank=True,null=True,
                                               verbose_name=_('Request reservation'))

    fix_reserved_date = models.DateField(default= default_reservation_date, null=True, blank=True,
                                         verbose_name=_('fixed date'))
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE, verbose_name=_('Operation type'), null=True,
                                  blank=True)
    volume = models.IntegerField(verbose_name=_('Material volume'), null=True, blank=True)
    unit = models.CharField(choices=Unit, max_length=15, verbose_name=_('Unit of calculation'), null=True, blank=True)
    start_session = models.TimeField(verbose_name=_('From the clock'), null=True, blank=True, default='08:00')
    end_session = models.TimeField(verbose_name=_('Up to the hour'), null=True, blank=True, default='12:00')
    date_time_created = models.DateTimeField(auto_now_add=True, null=True)
    date_time_modified = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.id}) {self.request_reservation.user}"

    class Meta:
        verbose_name = _("Appointment booking")
