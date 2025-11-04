from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *
from .resources import *
from jalali_date.admin import ModelAdminJalaliMixin
from django.utils.html import format_html, format_html_join
from jalali_date import datetime2jalali, datetime2jalali
from django.utils.translation import gettext_lazy as _
from home.models import Time
from jalali_date import date2jalali
import jdatetime
from import_export.admin import ImportExportModelAdmin
from import_export.admin import ExportMixin
from config.admin_site import custom_admin_site


class WorkHourInline(admin.TabularInline):
    model = WorkHourReport
    extra = 0


class PayslipInline(admin.TabularInline):
    model = Payslip
    extra = 0


@admin.register(User, site=custom_admin_site)
class UserAdmin(ImportExportModelAdmin, BaseUserAdmin):

    resource_class = UserResources
    skip_admin_log = True
    list_display = ('id', 'phone_number', 'name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ['phone_number', 'name']
    ordering = ('phone_number',)
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('اطلاعات شخصی', {'fields': ('name',)}),
        ('دسترسی‌ها', {'fields': ('is_staff', 'is_active',
         'is_superuser', 'groups', 'user_permissions')}),
        ('تاریخ‌ها', {'fields': ('date_joined',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'name', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )

    def has_view_permission(self, request, obj=None):
        return True

    @admin.display(description=_('datetime joined'))
    def date_joined_jalali(self, obj):
        return datetime2jalali(obj.date_joined).strftime('%Y/%m/%d - %H:%M')


@admin.register(WorkHourReport, site=custom_admin_site)
class WorkHourReportAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = WorkHourReportResources
    skip_admin_log = True
    list_display = ('employee', 'year', 'month', 'duty_hours', 'overtime')
    list_filter = ('year', 'month')
    search_fields = ('employee__phone_number', 'employee__name')


@admin.register(Payslip, site=custom_admin_site)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ('employee', 'year', 'month', 'payslip_jalali_date')
    list_filter = ('year', 'month')
    search_fields = ('employee__phone_number', 'employee__name')

    @admin.display(description=_('تاریخ ایجاد'))
    def payslip_jalali_date(self, obj):
        return date2jalali(obj.date_created).strftime('%Y/%m/%d')


@admin.register(StaffProfile, site=custom_admin_site)
class StaffProfileAdmin(ExportMixin, ModelAdminJalaliMixin, admin.ModelAdmin):
    resource_classes = [StaffProfileExportResources]
    inlines = [WorkHourInline, PayslipInline]

    list_display = ('user', 'staff_jalali_birth_date',
                    'staff_joined_jalali_date')
    search_fields = ('employee__name',)

    @admin.display(description=_('تاریخ پیوستن'))
    def staff_joined_jalali_date(self, obj):
        return date2jalali(obj.date_joined).strftime('%Y/%m/%d')

    @admin.display(description="تاریخ تولد")
    def staff_jalali_birth_date(self, obj):
        if obj.birth_date:
            return date2jalali(obj.birth_date).strftime('%Y/%m/%d')
        return ""


# مشتری ها

class TicketReplyInline(admin.TabularInline):
    model = TicketReply
    extra = 1
    readonly_fields = ['responder', 'created_at']
    exclude = ['responder']

    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super().get_formset(request, obj, **kwargs)
        original_save_new = FormSet.save_new

        def save_new_with_responder(self2, form, commit=True):
            instance = original_save_new(self2, form, False)
            if not instance.responder_id:
                instance.responder = request.user
            if commit:
                instance.save()
                instance.ticket.status = 'answered'
                instance.ticket.save()
            return instance

        FormSet.save_new = save_new_with_responder
        return FormSet


@admin.register(SupportTicketProxy, site=custom_admin_site)
class SupportTicketProxyAdmin(admin.ModelAdmin):
    list_display = ['sender', 'title', 'created_jalali',
                    'time_created', 'colored_status']
    readonly_fields = ['created_jalali',
                       'status', 'title', 'sender', 'message']
    search_fields = ['sender__name', 'status']
    list_filter = ['status']
    inlines = [TicketReplyInline]

    @admin.display(description="تاریخ ایجاد")
    def created_jalali(self, obj):
        return date2jalali(obj.created_at).strftime('%Y/%m/%d')

    @admin.display(description="وضعیت پاسخ")
    def colored_status(self, obj):
        if obj.status == 'answered':
            background = "#32CD32"
            text = 'پاسخ داده شده'
        else:
            background = "#FF0000"
            text = 'پاسخ داده نشده'
        return format_html(
            '<div style="background-color: {}; padding:4px 8px; border-radius:5px; text-align:center;">{}</div>',
            background,
            text
        )


# class SupportTicketAdmin(admin.ModelAdmin):
#     list_display = ['title', 'sender', 'support_jalali_date' ,'colored_status']
#     inlines = [TicketReplyInline]
#     list_filter = ['status']
#     readonly_fields = ['status']

#     @admin.display(description=_('تاریخ ایجاد'))
#     def support_jalali_date(self, obj):
#         return date2jalali(obj.created_at).strftime('%Y/%m/%d')


#     def colored_status(self,obj):
#         if obj.status=='answered':
#             background = "#32CD32"
#             text = 'پاسخ داده شده'
#         else:
#             background = "#FF0000"
#             text = 'پاسخ داده نشده'
#         return format_html(
#             '<div style="background-color: {}; padding:4px 8px; border-radius:5px; text-align:center;">{}</div>',
#             background,
#             text
#         )

#     colored_status.short_description = 'وضعیت'


# admin.site.register(SupportTicket, SupportTicketAdmin)

# class TicketReplyAdmin(admin.ModelAdmin):
#     list_display = ['ticket','responder','reply_admin_jalali_date']
#     list_filter = ['created_at']

#     def save_model(self, request, obj, form, change):
#         if not obj.responder_id:
#             obj.responder = request.user  # مقداردهی responder به کاربر جاری
#         super().save_model(request, obj, form, change)

#     @admin.display(description=_('تاریخ ایجاد'))
#     def reply_admin_jalali_date(self,obj):
#         return date2jalali(obj.created_at).strftime('%Y/%m/%d')

# admin.site.register(TicketReply,TicketReplyAdmin)

@admin.register(Invoice, site=custom_admin_site)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['customer', 'invoice_jalali_date', 'invoice_preview']
    list_filter = ['created_date']

    @admin.display(description=_('پیش‌نمایش فاکتور'))
    def invoice_preview(self, obj):
        if obj.invoice and obj.invoice.url.lower().endswith(('.png', '.jpg', '.jpeg')):
            return format_html('<img src="{}" width="200" />', obj.invoice.url)
        elif obj.invoice and obj.invoice.url.lower().endswith('.pdf'):
            return format_html('<a href="{}" target="_blank">مشاهده PDF</a>', obj.invoice.url)
        return "فایلی بارگذاری نشده"

    @admin.display(description=_('تاریخ ایجاد'))
    def invoice_jalali_date(self, obj):
        return date2jalali(obj.created_date).strftime('%Y/%m/%d')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'customer':
            kwargs["queryset"] = CustomerProfile.objects.filter(
                user__is_staff=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class InvoiceInline(admin.TabularInline):
    model = Invoice
    extra = 0
    readonly_fields = ('invoice', 'created_date')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(CustomerProfile, site=custom_admin_site)
class CustomerProfileAdmin(ExportMixin, admin.ModelAdmin):
    resource_classes = [CustomerProfileExportResources]
    list_display = ['user',]
    readonly_fields = ['show_reserve_history', 'show_tikets']
    inlines = [InvoiceInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user__is_staff=False)

    def show_reserve_history(self, obj):
        # استفاده از prefetch_related برای کاهش تعداد query ها
        times = Time.objects.filter(
            request_reservation__user=obj.user).order_by('-fix_reserved_date')

        if not times.exists():
            return "رزروی ثبت نشده"

        return format_html(
            "<ul>{}</ul>",
            format_html_join(
                "",
                "<li>{}</li>",
                (
                    (
                        jdatetime.datetime.fromgregorian(
                            datetime=t.fix_reserved_date)
                        .strftime("%Y/%m/%d %H:%M"),
                    ) for t in times
                )
            )
        )
    show_reserve_history.short_description = "تاریخچه رزروها"

    # نمایش تاریخچه تیکت‌ها

    def show_tikets(self, obj):
        tickets = SupportTicket.objects.filter(
            sender=obj.user).order_by('-created_at')

        if not tickets.exists():
            return "تیکتی وجود ندارد"

        return format_html(
            "<ul>{}</ul>",
            format_html_join(
                "",
                "<li>{}</li>",
                (
                    (
                        jdatetime.datetime.fromgregorian(datetime=t.created_at)
                        .strftime("%Y/%m/%d %H:%M"),
                    ) for t in tickets
                )
            )
        )
    show_tikets.short_description = "تاریخچه تیکت‌ها"


# Employee Tickets

# @admin.register(EmployeeTicket)
# class EmployeeTicketAdmin(admin.ModelAdmin):
#     list_display = (
#         "id", "employee", "ticket_type",
#         "leave_start", "leave_end", "facility_amount",
#         "advance_amount", "create_employee_ticket_jalali_date"
#     )
#     list_filter = ("ticket_type", "created_at")
#     search_fields = ("employee__username", "employee__first_name", "employee__last_name")

#     fieldsets = (
#         ("اطلاعات عمومی", {
#             "fields": ("employee", "ticket_type", "description")
#         }),
#         ("مرخصی", {
#             "fields": ("leave_start", "leave_end", "leave_type"),
#             "classes": ("collapse",)  # جمع‌شونده
#         }),
#         ("تسهیلات", {
#             "fields": ("facility_amount", "facility_duration_months"),
#             "classes": ("collapse",)
#         }),
#         ("مساعده", {
#             "fields": ("advance_amount",),
#             "classes": ("collapse",)
#         }),
#         ("زمان‌ها", {
#             "fields": ("create_employee_ticket_jalali_date", "updated_at"),
#         }),
#     )

#     readonly_fields = ("create_employee_ticket_jalali_date", "updated_at")

#     @admin.display(description=_('تاریخ ایجاد'))
#     def create_employee_ticket_jalali_date(self,obj):
#         return date2jalali(obj.created_at).strftime('%Y/%m/%d')

#     def last_reply_status(self, obj):
#         last_reply = obj.replies.order_by('-created_at').first()
#         if last_reply:
#             # برگرداندن متن وضعیت آخرین ریپلای با رنگ
#             if last_reply.status == 'agreed':
#                 bg = '#32CD32'
#                 text = 'موافقت شده'
#             elif last_reply.status == 'in_progress':
#                 bg = '#007bff'
#                 text = 'در حال بررسی'
#             else:
#                 bg = '#FF0000'
#                 text = 'رد شده'
#             return format_html(
#                 '<div style="background-color:{}; padding:4px 8px; border-radius:5px; text-align:center;">{}</div>',
#                 bg, text
#             )
#         return "-"

#     last_reply_status.short_description = "وضعیت آخرین پاسخ"


# @admin.register(EmployeeTicketReply)
# class EmployeeTicketReplyAdmin(admin.ModelAdmin):
#     list_display = (
#         "id",
#         "ticket",
#         "author",
#         "replay_employee_jalali_date",
#         "status_colored_ticket",
#         "read_status_colored"
#     )
#     list_filter = ("is_read", "created_at", "author", "status_ticket")
#     search_fields = ("author__username", "author__first_name", "author__last_name", "ticket__employee__username")
#     readonly_fields = ("created_at", "author", "is_read" ,"status")
#     exclude = ['author']

#     fieldsets = (
#         ("اطلاعات پاسخ", {
#             "fields": ("ticket", "message", "is_read" ,"status_ticket")
#         }),
#         ("زمان‌ها", {
#             "fields": ("created_at",),
#         }),
#     )

#     @admin.display(description=_('تاریخ ایجاد'))
#     def replay_employee_jalali_date(self, obj):
#         return date2jalali(obj.created_at).strftime('%Y/%m/%d')

#     def status_colored_ticket(self, obj):
#         if obj.status_ticket == 'agreed':
#             bg = '#32CD32'
#             text = 'موافقت شده'
#         elif obj.status_ticket == 'in_progress':
#             bg = '#007bff'
#             text = 'در حال بررسی'
#         else:
#             bg = '#FF0000'
#             text = 'رد شده'
#         return format_html(
#             '<div style="background-color:{}; padding:4px 8px; border-radius:5px; text-align:center;">{}</div>',
#             bg, text
#         )
#     status_colored_ticket.short_description = "وضعیت درخواست"

#     def save_model(self, request, obj, form, change):
#         if not obj.pk:
#             obj.author = request.user
#         super().save_model(request, obj, form, change)

#     def read_status_colored(self, obj):
#         if obj.status:
#             background = "#32CD32"
#             text = 'پاسخ داده شده'
#         else:
#             background = "#FFB700"
#             text = 'در انتظار پاسخ'
#         return format_html(
#             '<div style="background-color: {}; padding:4px 8px; border-radius:5px; text-align:center;">{}</div>',
#             background, text
#         )
#     read_status_colored.short_description = 'وضعیت پاسخ'


class EmployeeTicketReplyInline(admin.TabularInline):
    model = EmployeeTicketReply
    extra = 0
    readonly_fields = ('author', 'created_at')
    fields = ('author', 'message', 'file', 'status_ticket', 'created_at')
    show_change_link = True

    def save_new_instance(self, obj, request):
        if not obj.pk:
            obj.author = request.user
            obj.save()
            obj.ticket.status = 'answered'
            obj.ticket.save()

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)
        if not change:
            obj.ticket.status = 'answered'
            obj.ticket.save()

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        original_save_new = formset.save_new

        def save_new_with_author(self, form, commit=True):
            instance = original_save_new(self, form, False)  # save=False
            if not instance.author_id:
                instance.author = request.user
            if commit:
                instance.save()
            return instance

        formset.save_new = save_new_with_author
        return formset


@admin.register(EmployeeTicketProxy, site=custom_admin_site)
class EmployeeTicketProxyAdmin(admin.ModelAdmin):
    list_display = (
        'employee__name', 'ticket_type', 'leave_start_jalali', 'leave_end_jalali', 'created_jalali', 'time_created',
        'status_colored', 'status_colored_ticket', 'description'
    )
    search_fields = ('employee__username',
                     'employee__first_name', 'employee__last_name')
    list_filter = ('ticket_type',)
    inlines = [EmployeeTicketReplyInline]
    exclude = ('leave_start', 'leave_end',)
    readonly_fields = ('leave_start_jalali', 'leave_end_jalali',
                       'created_jalali', 'time_created', 'ticket_type', 'description')

    fieldsets = (
        ('اطلاعات عمومی', {
            'fields': ('employee', 'ticket_type', 'description')
        }),
        ('مرخصی', {
            'fields': ('leave_type', 'leave_start_jalali', 'leave_end_jalali'),
        }),
        ('زمان‌ها', {
            'fields': ('created_jalali', 'time_created'),
        }),
    )

    @admin.display(description="تاریخ ایجاد")
    def created_jalali(self, obj):
        return date2jalali(obj.created_at).strftime('%Y/%m/%d')

    @admin.display(description="وضعیت پاسخ")
    def status_colored(self, obj):
        last_reply = obj.replies.order_by('-created_at').first()
        if last_reply and last_reply.author.is_staff:
            bg = "#32CD32"
            text = "پاسخ داده شده"
        else:
            bg = "#FFB700"
            text = "پاسخ داده نشده"
        return format_html(
            '<div style="background-color:{}; padding:4px 8px; border-radius:5px; text-align:center;">{}</div>',
            bg, text
        )

    @admin.display(description="وضعیت درخواست")
    def status_colored_ticket(self, obj):
        last_reply = obj.replies.order_by('-created_at').first()
        if not last_reply:
            bg, text = '#007bff', 'در حال بررسی'
        else:
            if last_reply.status_ticket == 'agreed':
                bg, text = '#32CD32', 'موافقت شده'
            elif last_reply.status_ticket == 'in_progress':
                bg, text = '#007bff', 'در حال بررسی'
            else:
                bg, text = '#FF0000', 'رد شده'
        return format_html(
            '<div style="background-color:{}; padding:4px 8px; border-radius:5px; text-align:center;">{}</div>',
            bg, text
        )

    @admin.display(description="شروع مرخصی")
    def leave_start_jalali(self, obj):
        if obj.leave_start:
            return date2jalali(obj.leave_start).strftime('%Y/%m/%d')
        return "-"

    @admin.display(description="پایان مرخصی")
    def leave_end_jalali(self, obj):
        if obj.leave_end:
            return date2jalali(obj.leave_end).strftime('%Y/%m/%d')
        return "-"

    def save_model(self, request, obj, form, change):

        obj._admin_override = True
        super().save_model(request, obj, form, change)


@admin.register(Suggestion, site=custom_admin_site)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "user_type",
                    "get_shamsi_date", "is_reviewed")
    list_filter = ("user_type", "is_reviewed",)
    search_fields = ("title", "text", "user__name")
    readonly_fields = ('user', 'user_type', 'title',
                       'text', "get_shamsi_date",)

    @admin.display(description='تاریخ ایجاد')
    def get_shamsi_date(self, obj):
        return date2jalali(obj.created_at).strftime('%Y/%m/%d')

    def get_object(self, request, object_id, from_field=None):
        obj = super().get_object(request, object_id, from_field)
        if obj and not obj.is_reviewed:
            obj.is_reviewed = True
            obj.save(update_fields=["is_reviewed"])
        return obj
