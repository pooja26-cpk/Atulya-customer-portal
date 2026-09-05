import frappe
from frappe.utils import formatdate
from .get_base_context import get_base_context

def get_context(context):
    context = get_base_context(context)
    context.title = "Support"
    context.pathname = "/support"
    
    if not context.get('customer_id') or context.customer_id == "Not Linked":
        context.open_tickets = []
        return context
        
    try:
        ticket_limit = int(frappe.form_dict.get("ticket_limit", 5))
    except (ValueError, TypeError):
        ticket_limit = 5

    context.ticket_limit = ticket_limit
    context.has_more_tickets = False
    context.total_tickets_count = frappe.db.count("Customer Support Request", filters={"customer": context.customer_id})
    
    issues = frappe.get_all(
        "Customer Support Request",
        filters={"customer": context.customer_id},
        fields=["name", "subject", "status", "creation"],
        order_by="creation desc",
        limit=ticket_limit + 1
    )
    
    if len(issues) > ticket_limit:
        context.has_more_tickets = True
        issues = issues[:ticket_limit]

    for issue in issues:
        issue.formatted_date = formatdate(issue.creation, "dd MMM yy")
        if issue.status in ["Open", "In Progress"]:
            issue.status_badge = issue.status
            issue.status_color = "warning"
        elif issue.status in ["Resolved", "Closed"]:
            issue.status_badge = issue.status
            issue.status_color = "success"
        else:
            issue.status_badge = issue.status
            issue.status_color = "neutral"
            
    context.open_tickets = issues
    return context
