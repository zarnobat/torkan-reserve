from django.contrib import admin
from django.utils.html import format_html
from jalali_date import date2jalali
from .models import LabResult
from config.admin_site import custom_admin_site


@admin.register(LabResult, site=custom_admin_site)
class LabResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'serial_number', 'get_shamsi_date', 'file_preview')
    readonly_fields = ('serial_number', 'created_at', 'file_preview')
    search_fields = ('user__username', 'serial_number')
    list_filter = ('created_at',)

    @admin.display(description='تاریخ ایجاد')
    def get_shamsi_date(self, obj):
        return date2jalali(obj.created_at).strftime('%Y/%m/%d')

    def file_preview(self, obj):
        if not obj.file:
            return "فاقد فایل"

        file_url = obj.file.url
        ext = obj.file.name.split('.')[-1].lower()

        if ext in ["jpg", "jpeg", "png", "gif", "webp"]:
            return format_html(
                '<img src="{}" width="200" style="object-fit: contain; border:1px solid #ddd; padding:4px; border-radius:8px;" />',
                file_url
            )

        if ext == "pdf":
            return format_html(
                '<a href="{}" target="_blank" style="color:blue; font-weight:bold;">دانلود فایل PDF</a>',
                file_url
            )

        return format_html(
            '<a href="{}" target="_blank">دانلود فایل</a>',
            file_url
        )

    file_preview.short_description = "پیش‌نمایش فایل"