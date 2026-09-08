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
        fields=["name", "posting_date", "transporter", "lr_no", "status", "lr_date"],
        order_by="posting_date desc",
        limit_page_length=limit + 1
    )
    
    if len(delivery_notes) > limit:
        context.has_more = True
        delivery_notes = delivery_notes[:limit]

    for dn in delivery_notes:
        dn.date = formatdate(dn.posting_date, "dd MMM yyyy")
        
        # Count items
        items_count = frappe.db.count("Delivery Note Item", {"parent": dn.name})
        dn.total_items = f"{items_count} items"

        # Get Sales Order reference
        so_ref = frappe.db.get_value("Delivery Note Item", {"parent": dn.name}, "against_sales_order")
        dn.order_ref = so_ref if so_ref else "—"

        # Set ETA based on lr_date or Sales Order delivery_date
        if dn.lr_date:
            dn.eta = formatdate(dn.lr_date, "dd MMM yyyy")
        elif so_ref:
            so_delivery_date = frappe.db.get_value("Sales Order", so_ref, "delivery_date")
            dn.eta = formatdate(so_delivery_date, "dd MMM yyyy") if so_delivery_date else "—"
        else:
            dn.eta = "—"
        
        # Map status to a user-friendly format
        if dn.status == "Completed":
            dn.status_badge = "Delivered"
        elif dn.status in ["To Bill", "In Transit", "Partially Billed"]:
            dn.status_badge = "Shipped"
        elif dn.status == "Return":
            dn.status_badge = "Returned"
        else:
            dn.status_badge = "Pending"
    
    context.delivery_notes = delivery_notes
    return context