from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from config.admin_site import custom_admin_site

urlpatterns = [
    path("admin/", custom_admin_site.urls),
    path('', include('home.urls')),
    path('accounts/', include('accounts.urls')),
    path('article/', include('article.urls')),
    path('tasks/', include('tasks.urls')),
    path('laboratory/', include('laboratory.urls')),
    # CKEditor
    path("ckeditor/", include("ckeditor_uploader.urls")),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
        # Rosetta (i18n)
        path('rosetta/', include('rosetta.urls')),
    ]
