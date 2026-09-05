import frappe
from frappe.utils import formatdate, fmt_money

def get_context(context):
    """
    Get the context for the My Profile page.
    """
    user = frappe.session.user
    # Get the current contact
    contact_name = frappe.db.get_value("Contact", {"user": user}, "name")
    if not contact_name:
        contact_name = frappe.db.get_value("Contact", {"email_id": user}, "name")

    customer_id = None
    if contact_name:
        # Get customer linked to the contact via Dynamic Link
        customer_id = frappe.db.get_value(
            "Dynamic Link",
            {"parenttype": "Contact", "parent": contact_name, "link_doctype": "Customer"},
            "link_name",
        )
        
    if not customer_id:
        customer_id = frappe.db.get_value("Portal User", {"user": user, "parenttype": "Customer"}, "parent")
        
    if not customer_id:
        frappe.throw("Customer not found for the current user.", frappe.DoesNotExistError)
    
    context.customer_id = customer_id
    context.pathname = "/my-profile"
    
    # Fetch customer and contact details
    customer = frappe.get_doc("Customer", customer_id)
    contact = frappe.get_doc("Contact", contact_name) if contact_name else None
    
    context.customer = customer
    context.contact = contact
    
    # Format data for display
    context.customer_since = formatdate(customer.creation, "MMM yyyy")
    credit_limit = frappe.db.get_value("Customer Credit Limit", {"parent": customer_id}, "credit_limit") or 0
    context.credit_limit = fmt_money(credit_limit, currency=customer.default_currency or "INR")
    
    # Get additional details
    sales_team = frappe.get_all("Sales Team", filters={"parent": customer.name, "parenttype": "Customer"}, fields=["sales_person"])
    if sales_team:
        context.salesman = frappe.db.get_value("Sales Person", sales_team[0].sales_person, "sales_person_name")
    else:
        context.salesman = None
        
    # Get PAN number from customer
    context.pan_number = customer.pan or ""

    return context