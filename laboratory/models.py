from django.db import models
from django.contrib.auth import get_user_model
import uuid
import os

User = get_user_model()

def lab_file_path(instance, filename):
    
    ext = filename.split('.')[-1]
    filename = f"{instance.serial_number}.{ext}"
    return os.path.join('lab_results', instance.serial_number, filename)


class LabResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="کاربر")
    serial_number = models.CharField(max_length=6, unique=True, editable=False, verbose_name="شماره سریال")
    file = models.FileField(upload_to=lab_file_path, verbose_name="فایل")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    def is_pdf(self):
        if not self.file:
            return False
        return self.file.name.lower().endswith(".pdf")

    def save(self, *args, **kwargs):
        if not self.serial_number :
            self.serial_number = str(uuid.uuid4().int)[:6]  
        super().save(*args, **kwargs)

    def __str__(self):
        return f"نتیجه آزمایش برای کاربر {self.user} با شماره سریال {self.serial_number} ایجاد شد."
    
    class Meta:
        verbose_name = "جواب آژمایش"
        verbose_name_plural = "جواب های آزمایش ها"