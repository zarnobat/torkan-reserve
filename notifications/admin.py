from django.contrib import admin
from .models import Notification , SMS
from jalali_date import date2jalali


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("message", "receiver", "get_shamsi", 'time',"is_read")
    list_filter = ("is_read" ,"created_at")
    
    @admin.display(description='تاریخ ایجاد')
    def get_shamsi(self,obj):
        return date2jalali(obj.created_at).strftime('%Y/%m/%d')
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        # وقتی ادمین وارد صفحه جزئیات می‌شود، is_read رو True می‌کنیم
        obj = self.get_object(request, object_id)
        if obj and not obj.is_read:
            obj.is_read = True
            obj.save()
        return super().change_view(request, object_id, form_url, extra_context)

    # class Media:
    #     js = ("notifications/js/notifications.js",)
                

@admin.register(SMS)
class SmsAdmin(admin.ModelAdmin):
    list_display = ['receiver', 'message', 'get_shamsi']
    list_filter = ['created_at']

    @admin.display(description='تاریخ ایجاد')
    def get_shamsi(self,obj):
        return date2jalali(obj.created_at).strftime('%Y/%m/%d')