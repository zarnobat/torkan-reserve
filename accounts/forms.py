from django.contrib.auth.forms import UserChangeForm
from .models import User, SupportTicket, EmployeeTicket, Suggestion
from django import forms
from jalali_date.fields import JalaliDateField
from jalali_date.widgets import AdminJalaliDateWidget
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.template.loader import get_template
import datetime


class FlatJalaliDateWidget(AdminJalaliDateWidget):
    template_name = "widgets/flat_jalali_input.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        return context

    def render(self, name, value, attrs=None, renderer=None):
        # Use the template from the main templates directory
        template = get_template(self.template_name)
        context = self.get_context(name, value, attrs)
        return template.render(context)


class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label=_('Password'), widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(
        label=_('Confirm password'), widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ('phone_number', 'name', 'is_superuser',)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        is_superuser = cleaned_data.get("is_superuser")
        if is_superuser:
            if not password1:
                raise forms.ValidationError(
                    "رمز عبور برای مدیر (superuser) الزامی است.")
            if password1 != password2:
                raise forms.ValidationError(
                    "رمز عبور و تکرار آن یکسان نیستند.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    password1 = forms.CharField(
        label='Password1', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(
        label="Confirm Password", widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ('phone_number', 'name', 'is_superuser',)

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password1 = self.cleaned_data.get('password1')
        if password1:
            user.set_password(password1)
        if commit:
            user.save()
            self.save_m2m()
        return user


class PhoneNumberForm(forms.ModelForm):

    class Meta:
        model = get_user_model()
        fields = ['name', 'phone_number']

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get('phone_number')
        name = cleaned_data.get('name')
        if not phone_number:
            raise forms.ValidationError("The phone number cannot be empty.")
        if not phone_number.startswith('09'):
            raise forms.ValidationError(
                "The phone number must start with '09'.")
        if len(phone_number) != 11:
            raise forms.ValidationError(
                "The phone number must be 11 digits long.")
        if not name:
            raise forms.ValidationError("The name cannot be empty.")
        return cleaned_data

    def validate_unique(self):
        """
        Override the unique check so that form doesn't raise error
        if phone_number already exists.
        """
        pass


class VerificationCodeForm(forms.Form):

    verification_code = forms.CharField(
        max_length=4, required=False, label='کد اعتبار سنجی')


class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ('title', 'message')
        lables = {
            'title': 'موضوع تیکت',
            'message': 'متن پیام',
        }

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'عنوان تیکت'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'پیام خود را بنویسید...'
            }),
        }


class EmployeeTicketForm(forms.ModelForm):
    class Meta:
        model = EmployeeTicket
        fields = [
            "employee",
            "ticket_type",
            "leave_start",
            "leave_end",
            "leave_type",
            "facility_amount",
            "facility_duration_months",
            "advance_amount",
            "description",
        ]
        labels = {
            "employee": "کارمند",
            "ticket_type": "نوع تیکت",
            "leave_start": "تاریخ شروع مرخصی",
            "leave_end": "تاریخ پایان مرخصی",
            "leave_type": "نوع مرخصی",
            "facility_amount": "مبلغ تسهیلات (ریال)",
            "facility_duration_months": "مدت بازپرداخت (ماه)",
            "advance_amount": "مبلغ مساعده (ریال)",
            "description": "توضیحات",
        }
        widgets = {
            "ticket_type": forms.Select(attrs={"class": "form-select"}),
            "leave_type": forms.Select(attrs={"class": "form-select"}),
            "facility_amount": forms.TextInput(attrs={"class": "form-input"}),
            "facility_duration_months": forms.NumberInput(attrs={"class": "form-input"}),
            "advance_amount": forms.TextInput(attrs={"class": "form-input"}),
            "description": forms.Textarea(attrs={"class": "form-textarea", "rows": 4}),
            "employee": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Use JalaliDateField with AdminJalaliDateWidget for leave dates
        self.fields['leave_start'] = JalaliDateField(
            label=self.Meta.labels.get('leave_start', 'تاریخ شروع مرخصی'),
            widget=FlatJalaliDateWidget(
                attrs={"class": "form-input jalali-date-input"}),
            required=False,
            initial="",
        )
        self.fields['leave_end'] = JalaliDateField(
            label=self.Meta.labels.get('leave_end', 'تاریخ پایان مرخصی'),
            widget=FlatJalaliDateWidget(
                attrs={"class": "form-input jalali-date-input"}),
            required=False,
            initial="",
            help_text="تاریخ پایان مرخصی باید بعد از تاریخ شروع باشد.",
        )

        conditional_fields = [
            'leave_start', 'leave_end', 'leave_type',
            'facility_amount', 'facility_duration_months',
            'advance_amount', 'description'
        ]
        for field in conditional_fields:
            self.fields[field].required = False

        ticket_type = None
        if self.instance and self.instance.pk:
            ticket_type = self.instance.ticket_type
        elif 'ticket_type' in self.data:
            ticket_type = self.data.get('ticket_type')
        elif 'ticket_type' in kwargs:
            ticket_type = kwargs.pop('ticket_type', None)

        if ticket_type:
            if ticket_type == 'leave':
                self.fields['leave_start'].required = True
                self.fields['leave_start'].error_messages = {
                    'required': 'لطفاً تاریخ شروع مرخصی را وارد کنید.'}
                self.fields['leave_end'].required = True
                self.fields['leave_end'].error_messages = {
                    'required': 'لطفاً تاریخ پایان مرخصی را وارد کنید.'}
                self.fields['leave_type'].required = True
                self.fields['leave_type'].error_messages = {
                    'required': 'لطفاً نوع مرخصی را انتخاب کنید.'}
            elif ticket_type == 'facility':
                self.fields['facility_amount'].required = True
                self.fields['facility_amount'].error_messages = {
                    'required': 'لطفاً مبلغ تسهیلات را وارد کنید.'}
                self.fields['facility_duration_months'].required = True
                self.fields['facility_duration_months'].error_messages = {
                    'required': 'لطفاً مدت بازپرداخت را وارد کنید.'}
            elif ticket_type == 'advance':
                self.fields['advance_amount'].required = True
                self.fields['advance_amount'].error_messages = {
                    'required': 'لطفاً مبلغ مساعده را وارد کنید.'}
            elif ticket_type == 'other':
                self.fields['description'].required = True
                self.fields['description'].error_messages = {
                    'required': 'لطفاً توضیحات را وارد کنید.'}

        if not self.instance.pk:
            self.fields['ticket_type'].initial = ticket_type or 'other'
        else:
            self.fields['ticket_type'].initial = ticket_type or 'other'

    def clean_leave_start(self):
        leave_start = self.cleaned_data.get("leave_start")
        if leave_start < datetime.date.today():
            raise forms.ValidationError(
                "تاریخ شروع مرخصی نمی‌تواند در گذشته باشد.")
        return leave_start

    def clean_leave_end(self):
        leave_start = self.cleaned_data.get("leave_start")
        leave_end = self.cleaned_data.get("leave_end")
        if leave_end and leave_end < datetime.date.today():
            raise forms.ValidationError(
                "تاریخ پایان مرخصی نمی‌تواند در گذشته باشد.")
        elif leave_start and leave_end:
            if leave_end < leave_start:
                raise forms.ValidationError(
                    "تاریخ پایان مرخصی باید بعد از تاریخ شروع باشد.")
        return leave_end

    def clean_facility_amount(self):
        value = self.cleaned_data.get("facility_amount")
        if value in (None, ""):
            return None
        if isinstance(value, str):
            value = value.replace(",", "")
        try:
            return float(value)
        except (ValueError, TypeError):
            raise forms.ValidationError("مبلغ تسهیلات معتبر نیست")

    def clean_advance_amount(self):
        value = self.cleaned_data.get("advance_amount")
        if value in (None, ""):
            return None
        if isinstance(value, str):
            value = value.replace(",", "")
        try:
            return float(value)
        except (ValueError, TypeError):
            raise forms.ValidationError("مبلغ مساعده معتبر نیست")


class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ('title', 'text')
        labels = {
            'title': 'عنوان',
            'text': 'متن پیشنهاد/انتقاد',
        }

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'text': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
        }


class SendSMSForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea, label="پیام")
