import frappe
from frappe.utils import formatdate, getdate, nowdate
from .get_base_context import get_base_context

def get_context(context):
    context = get_base_context(context)
    context.title = "Payments"

    # Get unpaid invoices
    filters = {"customer": context.customer_id, "docstatus": 1, "status": ["in", ["Unpaid", "Overdue", "Partly Paid"]]}
    
    invoices = frappe.get_all(
        "Sales Invoice",
        filters=filters,
        fields=["name", "posting_date", "due_date", "grand_total", "outstanding_amount", "status", "currency"],
        order_by="due_date asc"
    )
    
    today = getdate(nowdate())
    total_outstanding = 0
    
    for inv in invoices:
        inv.formatted_due_date = formatdate(inv.due_date, "dd MMM yyyy") if inv.due_date else "—"
        inv.is_overdue = inv.due_date and getdate(inv.due_date) < today
        inv.outstanding_formatted = frappe.utils.fmt_money(inv.outstanding_amount, precision=0)
        
        total_outstanding += inv.outstanding_amount
        
        # Format the status label for display
        if inv.is_overdue:
            inv.display_status = "Overdue"
            inv.status_color = "var(--danger)"
        elif inv.status == "Partly Paid":
            inv.display_status = f"Partial — ₹{inv.outstanding_formatted} remaining"
            inv.status_color = "var(--neutral-400)"
        else:
            inv.display_status = f"Due {formatdate(inv.due_date, 'dd MMM')}"
            inv.status_color = "var(--neutral-400)"
            
    context.unpaid_invoices = invoices
    context.total_outstanding = frappe.utils.fmt_money(total_outstanding, precision=0)
    context.total_invoices_count = len(invoices)
    
    # Also fetch recent Payment Entries for Payment History
    payment_entries = frappe.get_all(
        "Payment Entry",
        filters={"party_type": "Customer", "party": context.customer_id, "docstatus": 1},
        fields=["name", "posting_date", "reference_no", "paid_amount", "status"],
        order_by="posting_date desc",
        limit=5
    )
    
    for pe in payment_entries:
        pe.formatted_date = formatdate(pe.posting_date, "dd MMM yy")
        pe.amount_formatted = frappe.utils.fmt_money(pe.paid_amount, precision=0)
        pe.ref_label = pe.reference_no if pe.reference_no else pe.name
        pe.status_label = "Cleared" if pe.status == "Submitted" else pe.status
        
    context.payment_history = payment_entries

    return context
