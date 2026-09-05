import frappe
from .get_base_context import get_base_context

def get_context(context):
    context = get_base_context(context)
    context.title = "New Order"
    context.pathname = "/new-order"
    
    if not context.get('customer_id') or context.customer_id == "Not Linked":
        frappe.throw("No customer linked to this user. Cannot place orders.")
        
    customer = context.customer_id
    
    # Fetch addresses linked to this customer
    # In Frappe, addresses are linked via Dynamic Link
    address_links = frappe.get_all("Dynamic Link", 
        filters={"link_doctype": "Customer", "link_name": customer, "parenttype": "Address"},
        fields=["parent"])
        
    addresses = []
    if address_links:
        address_names = [link.parent for link in address_links]
        addresses = frappe.get_all("Address", 
            filters={"name": ["in", address_names]},
            fields=["name", "address_title", "address_line1", "city", "pincode", "is_primary_address", "is_shipping_address"])
            
    # Format addresses for display
    formatted_addresses = []
    default_billing = ""
    default_shipping = ""
    
    for addr in addresses:
        display = f"{addr.address_line1}, {addr.city} - {addr.pincode}"
        if addr.is_primary_address:
            display += " (Default Billing)"
            default_billing = addr.name
        if addr.is_shipping_address:
            display += " (Default Shipping)"
            default_shipping = addr.name
            
        formatted_addresses.append({
            "name": addr.name,
            "display": display,
            "is_billing": addr.is_primary_address,
            "is_shipping": addr.is_shipping_address
        })
        
    context.addresses = formatted_addresses
    context.default_billing = default_billing
    context.default_shipping = default_shipping
    
    return context
