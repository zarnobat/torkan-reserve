from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from notifications.admin_site import custom_admin_site

from accounts import admin_registry
from home import admin_registry
from notifications import admin_registry
from article import admin_registry
from django.http import JsonResponse




def health_check(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path("admin/", custom_admin_site.urls),
    path('', include('home.urls')),
    path('accounts/', include('accounts.urls')),
    path('article/', include('article.urls')),
    path('health/', health_check),
    # Rosetta (i18n)
    # path('rosetta/', include('rosetta.urls')),

    # CKEditor
    path("ckeditor/", include("ckeditor_uploader.urls")),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)