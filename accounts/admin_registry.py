from notifications.admin_site import custom_admin_site
from .admin import (
    User, UserAdmin,
    WorkHourReport, WorkHourReportAdmin,
    Payslip, PayslipAdmin,
    StaffProfile, StaffProfileAdmin,
    SupportTicketProxy, SupportTicketProxyAdmin,
    Invoice, InvoiceAdmin,
    CustomerProfile, CustomerProfileAdmin,
    EmployeeTicketProxy, EmployeeTicketProxyAdmin,
    Suggestion, SuggestionAdmin,
)


custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(WorkHourReport, WorkHourReportAdmin)
custom_admin_site.register(Payslip, PayslipAdmin)
custom_admin_site.register(StaffProfile, StaffProfileAdmin)
custom_admin_site.register(SupportTicketProxy, SupportTicketProxyAdmin)
custom_admin_site.register(Invoice, InvoiceAdmin)
custom_admin_site.register(CustomerProfile, CustomerProfileAdmin)
custom_admin_site.register(EmployeeTicketProxy, EmployeeTicketProxyAdmin)
custom_admin_site.register(Suggestion, SuggestionAdmin)

