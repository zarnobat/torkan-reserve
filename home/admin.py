from django.contrib import admin
import jdatetime
from jalali_date.admin import ModelAdminJalaliMixin, StackedInlineJalaliMixin
from jalali_date import date2jalali, datetime2jalali
from .models import Time, Operation, OperationSetting, RequestReservation
from .utils import send_reservation_sms
from django.utils.translation import gettext_lazy as _
from .forms import TimeAdminForm
from config.admin_site import custom_admin_site


@admin.register(Time, site=custom_admin_site)
class TimeAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    form = TimeAdminForm
    list_display = (
    'id', 'trans_request_reservation_date', 'format_date', 'start_session', 'volume', 'unit', 'datetime_saved')
    search_fields = ('request_reservation__user__name', 'request_reservation__user__phone_number')
    ordering = ('-fix_reserved_date',)
    # autocomplete_fields = ('request_reservation',)

    # def has_view_permission(self, request, obj=None):
    #     return True

    @admin.display(description=_('Reservation date'))
    def format_date(self, obj):
        return date2jalali(obj.fix_reserved_date).strftime('%Y/%m/%d')

    @admin.display(description=_('Request reservation date'))
    def trans_request_reservation_date(self, obj):
        return obj.request_reservation.user

    @admin.display(description=_('datetime saved'))
    def datetime_saved(self, obj):
        return datetime2jalali(obj.request_reservation.datetime_created).strftime('%Y/%m/%d - %H:%M')
    
    autocomplete_fields = ('request_reservation',)


@admin.register(Operation, site=custom_admin_site)
class OperationAdmin(admin.ModelAdmin):
    list_display = ['operation_name', ]
    search_fields = ['operation_name', ]


@admin.register(OperationSetting, site=custom_admin_site)
class OperationSettingAdmin(admin.ModelAdmin):
    list_display = ['Product', 'capacity_materials', 'unit_capacity', 'display_calculation', ]
    readonly_fields = ('display_calculation',)


# StackedInline part in admin for RequestReservation model
class TimeInline(StackedInlineJalaliMixin, admin.TabularInline):
    model = Time
    form = TimeAdminForm


@admin.register(RequestReservation, site=custom_admin_site)
class RequestReservationAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ['id', 'user', 'datetime_created_jalali', 'suggested_jalali_date', 'status', ]
    fields = ['suggested_jalali_date', 'suggested_reservation_time', 'user', 'explanation', 'status']
    search_fields = ['user__name', 'user__phone_number']
    ordering = ['-datetime_created', ]
    readonly_fields = ['suggested_jalali_date', 'suggested_reservation_time', 'explanation']
    inlines = [TimeInline]
    # autocomplete_fields = ['user']

    # def has_view_permission(self, request, obj=None):
    #     return True

    @admin.display(description=_('suggested_reservation_date'))
    def suggested_jalali_date(self, obj):
        return date2jalali(obj.suggested_reservation_date).strftime('%Y/%m/%d')

    @admin.display(description=_('datetime_created'))
    def datetime_created_jalali(self, obj):
        return date2jalali(obj.datetime_created.date()).strftime('%Y/%m/%d')
