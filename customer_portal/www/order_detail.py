import frappe
from frappe.utils import formatdate, format_time, get_datetime
from .get_base_context import get_base_context

def get_context(context):
    context = get_base_context(context)
    order_name = frappe.form_dict.name
    
    if not order_name:
        frappe.redirect_to_message("Order Not Found", "The requested order could not be found.")
        raise frappe.Redirect
        
    try:
        order = frappe.get_doc("Sales Order", order_name)
    except frappe.DoesNotExistError:
        frappe.redirect_to_message("Order Not Found", "The requested order could not be found.")
        raise frappe.Redirect
        
    if order.customer != context.customer_id:
        frappe.redirect_to_message("Not Authorized", "You are not authorized to view this order.")
        raise frappe.Redirect
        
    context.title = f"Order {order.name}"
    
    if order.docstatus == 0:
        order.status = "Pending Approval"
        
    context.order = order
    
    context.formatted_date = formatdate(order.transaction_date, "dd MMM yyyy")
    
    # Format amount
    context.formatted_grand_total = frappe.utils.fmt_money(order.grand_total, currency=order.currency)
    context.formatted_total_taxes = frappe.utils.fmt_money(order.total_taxes_and_charges, currency=order.currency)
    context.formatted_net_total = frappe.utils.fmt_money(order.net_total, currency=order.currency)

    # Fetch Invoice
    invoice = frappe.db.get_value("Sales Invoice Item", {"sales_order": order.name}, "parent")
    context.invoice_name = invoice

    # Fetch Delivery Note
    delivery = frappe.db.get_value("Delivery Note Item", {"against_sales_order": order.name}, "parent")
    context.delivery_name = delivery
    
    # Transporter Details (from Delivery Note if exists)
    if delivery:
        dn_doc = frappe.get_doc("Delivery Note", delivery)
        context.transporter = dn_doc.transporter_name or dn_doc.transporter or "—"
        context.tracking_no = dn_doc.lr_no or "—"
        context.eta = formatdate(dn_doc.get("lr_date") or order.delivery_date, "dd MMM yyyy") if (dn_doc.get("lr_date") or order.delivery_date) else "—"
    else:
        context.transporter = "—"
        context.tracking_no = "—"
        context.eta = formatdate(order.delivery_date, "dd MMM yyyy") if order.delivery_date else "—"

    # Timeline Logic
    creation_dt = get_datetime(order.creation)
    context.timeline = {
        "placed_date": formatdate(creation_dt, "dd MMM yyyy"),
        "placed_time": format_time(creation_dt, "hh:mm A")
    }
    
    if order.status not in ["Draft", "Cancelled"]:
        context.timeline["confirmed_date"] = context.timeline["placed_date"]
        context.timeline["confirmed_time"] = context.timeline["placed_time"]
    
    if delivery:
        context.timeline["dispatched_date"] = formatdate(dn_doc.posting_date, "dd MMM yyyy")
        context.timeline["dispatched_time"] = format_time(dn_doc.posting_time, "hh:mm A")
        
    return context
