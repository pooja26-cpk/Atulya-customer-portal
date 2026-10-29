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
        
        # Primary address of the customer is read-only on the portal
        primary_name = frappe.db.get_value("Customer", context.customer_id, "customer_primary_address")

        # Clean datetime objects for JSON serialization
        for addr in addresses:
            addr["is_primary"] = 1 if (primary_name and addr.name == primary_name) else 0
            for key, value in addr.items():
                if hasattr(value, 'isoformat'):
                    addr[key] = str(value)
                    
        context.addresses = addresses
    else:
        context.addresses = []

    return context