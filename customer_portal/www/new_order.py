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
            fields=["name", "address_title", "address_type", "address_line1", "city", "pincode", "is_primary_address", "is_shipping_address"])
            
    # Format addresses for display
    billing_addresses = []
    shipping_addresses = []
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
            
        addr_data = {
            "name": addr.name,
            "display": display,
            "is_billing": addr.is_primary_address,
            "is_shipping": addr.is_shipping_address
        }
        
        # Categorize based on address_type. If empty, maybe put in both just in case.
        if addr.address_type in ("Billing", "Billing Address"):
            billing_addresses.append(addr_data)
        elif addr.address_type in ("Shipping", "Shipping Address"):
            shipping_addresses.append(addr_data)
        else:
            # Fallback if address_type is not strictly Billing or Shipping
            billing_addresses.append(addr_data)
            shipping_addresses.append(addr_data)
        
    context.billing_addresses = billing_addresses
    context.shipping_addresses = shipping_addresses
    context.default_billing = default_billing
    context.default_shipping = default_shipping
    context.uoms = frappe.get_all("UOM", fields=["name"])
    
    return context
