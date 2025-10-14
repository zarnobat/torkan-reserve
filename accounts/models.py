from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

class UserManager(BaseUserManager):
    def create_user(self, phone_number, name, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Users must have a phone number")
        if not name:
            raise ValueError("Users must have a name")
        user = self.model(phone_number=phone_number, name=name, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if not password:
            raise ValueError("Superuser must have a password")
        if not phone_number:
            raise ValueError("Superuser must have a phone number")

        return self.create_user(phone_number, name='Admin', password=password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=20, unique=True,verbose_name=_('phone number'))
    name = models.CharField(max_length=100,verbose_name=_('First and last name'))
    is_active = models.BooleanField(default=True , verbose_name=_('is active ?'))
    is_staff = models.BooleanField(default=False, verbose_name=_('is staff ?'))
    is_superuser = models.BooleanField(default=False , verbose_name=_('is superuser ?'))
    date_joined = models.DateTimeField(default=timezone.now ,verbose_name=_('date joined'))

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

    def __str__(self):
        return f"    {_('user')}  {self.name}  ,  {self.phone_number}"
    

User = get_user_model()

class SupportTicket(models.Model):
    STATUS_CHOICES =[
        ('pending','در انتظار پاسخ'),
        ('answered','پاسخ داده شده'),
    ]

    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر ارسال‌کننده")
    title = models.CharField(max_length=100, verbose_name="عنوان")
    message = models.TextField(verbose_name="پیام")
    created_at = models.DateField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    time_created = models.TimeField(auto_now_add=True, verbose_name='زمان ایجاد' )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending',verbose_name='وضعیت')


    def __str__(self):
        return f"{self.sender.name} - {self.title}"
    
    @property
    def is_answered(self):
        return self.replies.exists()

    class Meta:
        verbose_name = "تیکت مشتری"
        verbose_name_plural = "تیکت‌های مشتریان"



class SupportTicketProxy(SupportTicket):
    class Meta:
        proxy = True
        verbose_name = "تیکت مشتری"
        verbose_name_plural = "تیکت مشتری ها"


class TicketReply(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name="replies")
    responder = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name="پاسخ‌دهنده"
                ,editable=False)
    message = models.TextField(verbose_name="پاسخ")
    created_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        # ذخیره پاسخ
        super().save(*args, **kwargs)
        # وضعیت تیکت را آپدیت کن
        if self.responder.is_staff:
            self.ticket.status = 'answered'



    def __str__(self):
        return f"پاسخ به تیکت {self.ticket.sender} توسط {self.responder.name}"
    
    class Meta:
        verbose_name = "پاسخ پشتیبانی"
        verbose_name_plural = "پاسخ های پشتیبانی"



class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="کاربر", editable=False)
    
    def __str__(self):
        return f"پروفایل {self.user.name}"

    class Meta:
        verbose_name = "پروفایل مشتری"
        verbose_name_plural = "پروفایل مشتری‌ها"


class Invoice(models.Model):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, verbose_name="کاربر")
    invoice = models.FileField(upload_to='invoices/', null=True, blank=True, verbose_name="فاکتور")
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "فاکتور"
        verbose_name_plural = "فاکتورها"

# کارمندان

class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default='',verbose_name="کارمند")
    birth_date = models.DateField(verbose_name="تاریخ تولد",null=True , blank=True)
    date_joined = models.DateField(verbose_name="تاریخ پیوستن",auto_now_add=True)

    class Meta:
        verbose_name = "پروفایل کارمند"
        verbose_name_plural = "پروفایل کارمند ها"

    def __str__(self):
        return f"{self.user.name} ({self.user.phone_number})"
    


class WorkHourReport(models.Model):

    MONTH_CHOICES = [
        (1, "فروردین"),
        (2, "اردیبهشت"),
        (3, "خرداد"),
        (4, "تیر"),
        (5, "مرداد"),
        (6, "شهریور"),
        (7, "مهر"),
        (8, "آبان"),
        (9, "آذر"),
        (10, "دی"),
        (11, "بهمن"),
        (12, "اسفند"),
    ]

    employee = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, verbose_name="کارمند")
    year = models.IntegerField(choices=[(y, str(y)) for y in range(1400, 1450)], verbose_name="سال")
    month = models.IntegerField(choices=MONTH_CHOICES, verbose_name="ماه")
    duty_hours = models.IntegerField(verbose_name="ساعت موظفی")
    overtime = models.IntegerField(verbose_name="اضافه کاری")

    class Meta:
        verbose_name = "گزارش ساعت کاری"
        verbose_name_plural = "گزارش‌های ساعت کاری"

    def __str__(self):
        return f"{self.employee.user.name} - {self.year}/{self.month}"
    
    def get_month_display_name(self):
        return dict(self.MONTH_CHOICES).get(self.month, "")
    


class Payslip(models.Model):

    MONTH_CHOICES = [
        (1, "فروردین"),
        (2, "اردیبهشت"),
        (3, "خرداد"),
        (4, "تیر"),
        (5, "مرداد"),
        (6, "شهریور"),
        (7, "مهر"),
        (8, "آبان"),
        (9, "آذر"),
        (10, "دی"),
        (11, "بهمن"),
        (12, "اسفند"),
    ]

    employee = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, verbose_name="کارمند")
    year = models.IntegerField(choices=[(y, str(y)) for y in range(1400, 1450)], verbose_name="سال")
    month = models.IntegerField(choices=MONTH_CHOICES, verbose_name="ماه")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    payslip_image = models.FileField(upload_to='payslip/', null=True, blank=True, verbose_name="فیش حقوقی")
    work_hour = models.OneToOneField(WorkHourReport, on_delete=models.CASCADE, verbose_name="گزارش کارکرد ماهانه")

    class Meta:
        verbose_name = "فیش حقوقی"
        verbose_name_plural = "فیش‌های حقوقی"

    def __str__(self):
        return f"فیش {self.employee.user.name} - {self.year}/{self.month}"



class EmployeeTicket(models.Model):
    class TicketType(models.TextChoices):
        LEAVE = "leave", "مرخصی"
        FACILITY = "facility", "تسهیلات"
        ADVANCE = "advance", "مساعده"
        OTHER = "other", "سایر"

    class LeaveType(models.TextChoices):
        SICK = "sick", "استعلاجی"
        ANNUAL = "annual", "استحقاقی"
        UNPAID = "unpaid", "بدون حقوق"

    employee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tickets",
        verbose_name="کارمند",
        help_text="کارمند ایجادکننده این تیکت را انتخاب کنید."
    )
    ticket_type = models.CharField(
        max_length=20,
        choices=TicketType.choices,
        verbose_name="نوع تیکت",
        help_text="نوع درخواست یا مشکل را انتخاب کنید."
    )

    # فیلدهای مرخصی
    leave_start = models.DateField(null=True, blank=True, verbose_name="تاریخ شروع مرخصی")
    leave_end = models.DateField(null=True, blank=True, verbose_name="تاریخ پایان مرخصی")
    leave_type = models.CharField(max_length=20, choices=LeaveType.choices, null=True, blank=True, verbose_name="نوع مرخصی")


    facility_amount = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, verbose_name="مبلغ تسهیلات")
    facility_duration_months = models.PositiveIntegerField(null=True, blank=True, verbose_name="مدت بازپرداخت (ماه)")

    advance_amount = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, verbose_name="مبلغ مساعده")

    description = models.TextField(null=True, blank=True, verbose_name="توضیحات")
    
    created_at = models.DateField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    time_created = models.TimeField(auto_now_add=True, verbose_name='زمان ایجاد')
    updated_at = models.DateField(auto_now=True, verbose_name="آخرین بروزرسانی")

    class Meta:
        ordering = ['created_at']
        verbose_name = "تیکت کارمند"
        verbose_name_plural = "تیکت های کارمندان"

    def generate_description(self):
        """توضیحات خودکار بر اساس نوع تیکت تولید می‌کند."""
        employee_name = self.employee.name

        if self.ticket_type == self.TicketType.LEAVE:
            if self.leave_type and self.leave_start and self.leave_end:
                return f"اینجانب {employee_name} درخواست مرخصی {self.get_leave_type_display()} از تاریخ {self.leave_start} تا تاریخ {self.leave_end} دارم."
            return ""

        elif self.ticket_type == self.TicketType.FACILITY:
            if self.facility_amount and self.facility_duration_months:
                return f"اینجانب {employee_name} تقاضای دریافت تسهیلات به مبلغ {self.facility_amount} و بازپرداخت {self.facility_duration_months} ماهه دارم."
            return ""

        elif self.ticket_type == self.TicketType.ADVANCE:
            if self.advance_amount:
                return f"اینجانب {employee_name} تقاضای مساعده به مبلغ {self.advance_amount} ریال دارم."
            return ""

        elif self.ticket_type == self.TicketType.OTHER:
            return self.description or ""

        return ""

    def save(self, *args, **kwargs):
        """توضیحات خودکار را هنگام ذخیره تنظیم می‌کند."""
        if self.ticket_type != self.TicketType.OTHER:
            self.description = self.generate_description()
        super().save(*args, **kwargs)
    


class EmployeeTicketReply(models.Model):
    ticket = models.ForeignKey(
        'EmployeeTicket',
        on_delete=models.CASCADE,
        related_name='replies',
        verbose_name="تیکت مرتبط",
        help_text="تیکتی که این پاسخ مربوط به آن است."
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="نویسنده پاسخ",
        help_text="نویسنده پاسخ (کارمند یا ادمین).",
        editable=False
    )
    message = models.TextField(
        verbose_name="متن پاسخ",
        help_text="متن پاسخ."
    )
    created_at = models.DateField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
        help_text="تاریخ و زمان ایجاد پاسخ."
    )
    file = models.FileField(
        upload_to='file/',
        null=True, blank=True,
        verbose_name="ضمیمه"
    )
    status_ticket = models.CharField(
        max_length=20,
        choices=[("agreed", "موافقت شده"), ("in_progress", "در حال بررسی"), ("rejected", "رد شده")],
        default="in_progress",
        verbose_name="وضعیت",
        help_text="وضعیت فعلی تیکت."
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name="خوانده شده",
        # help_text="آیا این پاسخ توسط گیرنده خوانده شده است؟"
    )
    status = models.CharField(max_length=20,
        choices=[('pending','در انتظار پاسخ'),('answered','پاسخ داده شده')],
        default='pending')
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.ticket.status = 'answered'
            self.ticket.save()
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "پاسخ تیکت کارمند"
        verbose_name_plural = "پاسخ‌های تیکت کارمندان"

    def __str__(self):
        return f"پاسخ توسط {self.author} در تاریخ {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class EmployeeTicketProxy(EmployeeTicket):
    class Meta:
        proxy = True
        verbose_name = "تیکت کارمند"
        verbose_name_plural = "تیکت‌ کارمند ها"
        


class Suggestion(models.Model):
    USER_TYPE_CHOICES = [
        ('customer','مشتری'),
        ('staff','کارمند'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="suggestions",verbose_name='کاربر')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES,verbose_name='نوع کاربر')
    title = models.CharField(max_length=200, verbose_name="عنوان")
    text = models.TextField(verbose_name="متن پیشنهاد/انتقاد")
    created_at = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False, verbose_name="بررسی شده",editable=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "انتقاد/پیشنهاد"
        verbose_name_plural = "انتقادات و پیشنهادات"

    def __str__(self):
        return f"{self.get_user_type_display()} - {self.title}"
    


