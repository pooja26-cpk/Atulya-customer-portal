import frappe
from frappe.utils import formatdate
from .get_base_context import get_base_context

def get_context(context):
    context = get_base_context(context)
    context.title = "Delivery Notes"
    
    try:
        limit = int(frappe.form_dict.get("limit", 10))
    except (ValueError, TypeError):
        limit = 10

    filters = {"customer": context.customer_id, "docstatus": 1}

    context.limit = limit
    context.has_more = False
    context.total_count = frappe.db.count("Delivery Note", filters=filters)

    # Fetch Delivery Notes
    delivery_notes = frappe.get_all(
        "Delivery Note",
        filters=filters,
        fields=["name", "posting_date", "transporter", "lr_no", "status"],
        order_by="posting_date desc",
        limit=limit + 1
    )
    
    if len(delivery_notes) > limit:
        context.has_more = True
        delivery_notes = delivery_notes[:limit]

    for dn in delivery_notes:
        dn.date = formatdate(dn.posting_date, "dd MMM yyyy")
        
        # Count items
        items_count = frappe.db.count("Delivery Note Item", {"parent": dn.name})
        dn.items = f"{items_count} items"

        # Get Sales Order reference
        so_ref = frappe.db.get_value("Delivery Note Item", {"parent": dn.name}, "against_sales_order")
        dn.order_ref = so_ref if so_ref else "—"

        # Dummy ETA for now
        dn.eta = "—"
        
        # Map status to a user-friendly format
        if dn.status == "Delivered":
            dn.status_badge = "Delivered"
        elif dn.status == "In Transit":
            dn.status_badge = "Shipped"
        else:
            dn.status_badge = "Pending"
    
    context.delivery_notes = delivery_notes
    return context