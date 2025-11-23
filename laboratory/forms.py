from django import forms

class SerialCheckForm(forms.Form):
    serial_number = forms.CharField(max_length=10, label="شماره سریال آزمایش")
