from import_export import resources, fields, results
from import_export.widgets import ForeignKeyWidget
from import_export import exceptions
from import_export.results import RowResult
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from .models import User, StaffProfile, CustomerProfile, WorkHourReport
import logging
import re


logger = logging.getLogger(__name__)


class UserResources(resources.ModelResource):
    phone_number = fields.Field(attribute="phone_number", column_name="شماره تلفن")
    name = fields.Field(attribute="name", column_name="نام و نام خانوادگی")
    password = fields.Field(attribute="password", column_name="رمز عبور")
    is_staff = fields.Field(attribute="is_staff", column_name="کارمند است؟")
    is_active = fields.Field(attribute="is_active", column_name="فعال است؟")

    class Meta:
        model = User
        import_id_fields = ("phone_number",)
        fields = ("phone_number", "name", "is_staff", "is_active", "password")
        skip_unchanged = True
        report_skipped = True

    # ---------------- Counters ----------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.created_count = 0
        self.updated_count = 0
        self.skipped_count = 0
        self.errors = []

    def before_import(self, dataset, **kwargs):
        """Reset counters"""
        self.created_count = 0
        self.updated_count = 0
        self.skipped_count = 0
        self.errors.clear()

    # ---------------- Validation Logic ----------------
    def before_import_row(self, row, **kwargs):
        """
        Prepare and validate each row before actual import.
        - Hash passwords for new users
        - Skip rows with missing phone number
        """
        phone = row.get("شماره تلفن")
        if not phone:
            msg = "❌ شماره تلفن خالی است"
            self.errors.append(msg)
            row["خطا"] = msg  # optional, in case you want to display it
            self.skipped_count += 1
            # Returning here will effectively skip this row
            return

        try:
            user_exists = User.objects.filter(phone_number=phone).exists()
            if not user_exists:
                # New user: ensure password is hashed
                if not row.get("رمز عبور"):
                    # Generate random password if empty
                    random_pass = get_random_string(length=8)
                    row["رمز عبور"] = make_password(random_pass)
                else:
                    # Hash given password
                    row["رمز عبور"] = make_password(row["رمز عبور"])
            else:
                # Existing user → keep password unchanged
                row.pop("رمز عبور", None)
        except Exception as e:
            msg = f"❌ خطا در پردازش شماره {phone}: {e}"
            self.errors.append(msg)
            self.skipped_count += 1
            return

    # ---------------- Report ----------------
    def after_import_instance(self, instance, new, **kwargs):
        """Count creations/updates"""
        if not kwargs.get("dry_run"):
            if new:
                self.created_count += 1
            else:
                self.updated_count += 1

    def get_report(self):
        return {
            "ایجاد جدید": self.created_count,
            "به‌روزرسانی": self.updated_count,
            "رد شده": self.skipped_count,
            "خطاها": self.errors,
        }

    def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        report = self.get_report()
        print("📄 گزارش ایمپورت:", report)
    

class StaffProfileExportResources(resources.ModelResource):
    user_name = fields.Field(attribute="user__name", column_name="نام")
    user_phone = fields.Field(attribute="user__phone_number", column_name="شماره تلفن")
    birth_date = fields.Field(attribute="birth_date", column_name="تاریخ تولد")
    date_joined = fields.Field(attribute="date_joined", column_name="تاریخ پیوستن")

    class Meta:
        model = StaffProfile
        fields = ("user_name", "user_phone", "birth_date", "date_joined")
        export_order = ("user_name", "user_phone", "birth_date", "date_joined")


class CustomerProfileExportResources(resources.ModelResource):
    name = fields.Field(attribute="user__name", column_name="نام و نام خانوادگی")
    phone_number = fields.Field(attribute="user__phone_number", column_name="شماره تلفن")

    class Meta:
        model = CustomerProfile
        import_id_fields = ('phone_number',)
        fields = ("name", "phone_number")
        export_order = ("name", "phone_number")

      
class WorkHourReportResources(resources.ModelResource):
    name = fields.Field(
        attribute="employee__user__name",
        column_name="نام و نام خانوادگی",
        readonly=True,)
    
    employee = fields.Field(
        attribute="employee",
        column_name="شماره تلفن",
        widget=ForeignKeyWidget(StaffProfile, 'user__phone_number')  # phone number from lookup
    )
    
    year = fields.Field(attribute="year", column_name="سال")
    month = fields.Field(attribute="month", column_name="ماه")
    duty_hours = fields.Field(attribute="duty_hours", column_name="ساعت موظفی")
    overtime = fields.Field(attribute="overtime", column_name="اضافه کاری")

    class Meta:
        model = WorkHourReport
        import_id_fields = ("employee", "year", "month")  # حالا با employee منحصربه‌فرد
        fields = ("name", "employee", "year", "month", "duty_hours", "overtime")
        skip_unchanged = True
        report_skipped = True


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.created_count = 0
        self.updated_count = 0
        self.skipped_count = 0
        self.errors = []

    def before_import(self, dataset, **kwargs):
        self.created_count = 0
        self.updated_count = 0
        self.skipped_count = 0

    def before_import_row(self, row, **kwargs):
        """for debug"""
        print("BEFORE_ROW:", row)

    def import_row(self, row, instance_loader, **kwargs):
        phone = row.get("شماره تلفن")

        row_result = results.RowResult()
        row_result.errors = []
        row_result.import_type = results.RowResult.IMPORT_TYPE_SKIP

        if not phone:
            self.skipped_count += 1
            self.errors.append("❌ شماره تلفن خالی است")
            return row_result  

        if not User.objects.filter(phone_number=phone).exists():
            self.skipped_count += 1
            self.errors.append(f"❌ کاربری با شماره {phone} یافت نشد")
            return row_result  

        return super().import_row(row, instance_loader, **kwargs)
            

    def skip_row(self, instance, original, row, import_validation_errors=None):
        phone = row.get("شماره تلفن")

        if not phone:
            self.skipped_count += 1
            self.errors.append("❌ شماره تلفن خالی است")
            return True

        if not User.objects.filter(phone_number=phone).exists():
            self.skipped_count += 1
            self.errors.append(f"❌ کاربری با شماره {phone} یافت نشد")
            return True

        if instance.employee is None:
            self.skipped_count += 1
            self.errors.append(f"❌ employee برای ردیف با phone {phone} set نشده")
            return True

        """Prevent duplicate records from being created."""
        if import_validation_errors is None:  
            existing = WorkHourReport.objects.filter(
                year=row.get("سال"),
                month=row.get("ماه"),
                employee=instance.employee
            ).exists()
            if existing:
                self.updated_count += 1
            else:
                self.created_count += 1

        return super().skip_row(instance, original, row, import_validation_errors=import_validation_errors)
    
    def get_report(self):
        return {
            "ایجاد جدید": self.created_count,
            "به روز رسانی": self.updated_count,
            "خطاها": self.errors
        }

    def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        report = self.get_report()
        print("📄 گزارش ایمپورت:", report)