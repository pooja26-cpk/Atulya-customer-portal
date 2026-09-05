import frappe
from .get_base_context import get_base_context

def get_context(context):
    context = get_base_context(context)
    context.title = "Addresses"
    context.pathname = "/addresses"
    
    if not context.customer_id or context.customer_id == "Not Linked":
        context.addresses = []
        return context

    # Fetch addresses linked to the customer
    links = frappe.get_all("Dynamic Link", 
        filters={"parenttype": "Address", "link_doctype": "Customer", "link_name": context.customer_id},
        fields=["parent"]
    )
    
    if links:
        address_names = [d.parent for d in links]
        addresses = frappe.get_all("Address", 
            filters={"name": ["in", address_names]},
            fields=["*"]
        )
        context.addresses = addresses
    else:
        context.addresses = []

    return context