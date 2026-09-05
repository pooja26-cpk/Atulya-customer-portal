import frappe
from .dashboard import _get_customer

@frappe.whitelist()
def get_invoices(status=None, from_date=None, to_date=None):
    cust = _get_customer()

    filters = {"customer": cust, "docstatus": 1}
    if from_date: filters["posting_date"] = [">=", from_date]
    if to_date:   filters["posting_date"] = ["<=", to_date]
    if status == "Paid":    filters["outstanding_amount"] = 0
    if status == "Unpaid":  filters["outstanding_amount"] = [">", 0]
    if status == "Overdue":
        filters["outstanding_amount"] = [">", 0]
        filters["due_date"] = ["<", frappe.utils.nowdate()]

    return frappe.get_all("Sales Invoice", filters=filters,
        fields=["name", "posting_date", "due_date",
                "po_no", "grand_total", "outstanding_amount",
                "status", "ewaybill"],
        order_by="posting_date desc", page_length=50)

@frappe.whitelist()
def get_invoice_pdf_url(invoice_name):
    # Verify this invoice belongs to the customer
    cust = _get_customer()
    owner = frappe.db.get_value("Sales Invoice", invoice_name, "customer")
    if owner != cust:
        frappe.throw("Not permitted", frappe.PermissionError)
    return f"/api/method/frappe.utils.weasyprint.download_pdf?doctype=Sales Invoice&name={invoice_name}"
