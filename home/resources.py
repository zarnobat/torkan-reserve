from import_export import resources, fields
from jalali_date import date2jalali
from .models import Time
import datetime

class TimeResources(resources.ModelResource):

    name = fields.Field(
        attribute="request_reservation__user__name",
        column_name="نام"
    )    

    phone_number = fields.Field(
        attribute="request_reservation__user__phone_number",
        column_name="شماره تلفن",
    )

    fixed_date = fields.Field(attribute="fix_reserved_date", column_name="تاریخ رزرو")
    time = fields.Field(attribute="start_session", column_name="زمان شروع")
    operation = fields.Field(attribute="operation", column_name="عملیات")

    class Meta:
        model = Time
        fields = ("name", "phone_number", "fixed_date", "time", "operation")
        export_order = ("name", "phone_number", "fixed_date", "time", "operation")
        ordering = ["fix_reserved_date"]

    def dehydrate_fixed_date(self, obj):
        return date2jalali(obj.fix_reserved_date).strftime('%Y/%m/%d')
    
    