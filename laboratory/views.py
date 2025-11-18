from django.shortcuts import render
from .models import LabResult
from .forms import SerialCheckForm


def view_lab_result(request):
    result = None
    error = None
    download_url = None

    if request.method == "POST":
        form = SerialCheckForm(request.POST)
        if form.is_valid():
            serial = form.cleaned_data['serial_number']
            try:
                result = LabResult.objects.get(serial_number=serial)

                if result.file.name.lower().endswith(".pdf"):
                    download_url = result.file.url

            except LabResult.DoesNotExist:
                error = "با این کد نتیجه‌ای وجود ندارد."
    else:
        form = SerialCheckForm()

    return render(request, "laboratory/result.html", {
        "form": form,
        "result": result,
        "error": error,
        "download_url": download_url
    })
