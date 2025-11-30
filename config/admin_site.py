from django.contrib.admin import AdminSite


class CustomAdminSite(AdminSite):
    site_header = "پنل مدیریت"
    site_title = "ادمین"
    index_title = "خوش آمدید"

    def each_context(self, request):
        context = super().each_context(request)
        context["custom_js"] = ["notifications/js/notifications.js"]
        context["cms_link"] = "/cms/"
        return context


custom_admin_site = CustomAdminSite(name="custom_admin")
