import frappe
from frappe.utils import format_datetime

def get_context(context):
    user = frappe.session.user
    if user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/notifications"
        raise frappe.Redirect
        
    notifications = frappe.get_all("Notification Log",
        filters={"for_user": user},
        fields=["name", "subject", "email_content", "document_type", "document_name", "read", "creation"],
        order_by="creation desc",
        limit=50
    )
    
    for n in notifications:
        n.time_formatted = format_datetime(n.creation, "dd MMM yyyy, h:mm a")
        
    context.notifications = notifications
