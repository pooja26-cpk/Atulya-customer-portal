import frappe
from frappe.utils import formatdate, flt, fmt_money
from .get_base_context import get_base_context

def get_context(context):
    context = get_base_context(context)
    context.title = "Make Payment"

    invoice_param = frappe.form_dict.get("invoice")
    invoices_param = frappe.form_dict.get("invoices")

    invoice_names = []

    if invoices_param:
        invoice_names = [name.strip() for name in invoices_param.split(",") if name.strip()]
    elif invoice_param:
        invoice_names = [invoice_param]

    context.invoice_names = invoice_names
    context.invoices = []
    total_outstanding = 0

    for inv_name in invoice_names:
        inv = frappe.get_doc("Sales Invoice", inv_name)
        inv.outstanding_formatted = fmt_money(inv.outstanding_amount, precision=0)
        context.invoices.append({
            "name": inv.name,
            "customer": inv.customer_name,
            "posting_date": formatdate(inv.posting_date, "dd MMM yyyy") if inv.posting_date else "—",
            "due_date": inv.due_date,
            "formatted_due_date": formatdate(inv.due_date, "dd MMM yyyy") if inv.due_date else "—",
            "grand_total_formatted": fmt_money(inv.grand_total, precision=0),
            "outstanding_amount": flt(inv.outstanding_amount),
            "outstanding_formatted": inv.outstanding_formatted,
        })
        total_outstanding += flt(inv.outstanding_amount)

    if not invoice_names:
        filters = {"customer": context.customer_id, "docstatus": 1, "outstanding_amount": [">", 0]}
        invoices = frappe.get_all(
            "Sales Invoice",
            filters=filters,
            fields=["name", "customer_name", "posting_date", "due_date", "grand_total", "outstanding_amount"],
            order_by="due_date asc"
        )
        for inv in invoices:
            inv.outstanding_formatted = fmt_money(inv.outstanding_amount, precision=0)
            inv.posting_date = formatdate(inv.posting_date, "dd MMM yyyy") if inv.posting_date else "—"
            inv.formatted_due_date = formatdate(inv.due_date, "dd MMM yyyy") if inv.due_date else "—"
            inv.grand_total_formatted = fmt_money(inv.grand_total, precision=0)
            context.invoices.append(inv)
            total_outstanding += flt(inv.outstanding_amount)

    context.total_outstanding = fmt_money(total_outstanding, precision=0)
    context.total_outstanding_raw = total_outstanding

    company = None
    if context.invoices:
        first_inv = frappe.get_doc("Sales Invoice", context.invoices[0]["name"])
        company = first_inv.company
    else:
        invoice = frappe.get_all(
            "Sales Invoice",
            filters={"customer": context.customer_id, "docstatus": 1, "outstanding_amount": [">", 0]},
            limit=1,
            fields=["company"]
        )
        company = invoice[0].company if invoice else None

    context.company = company

    if company:
        bank_accts = frappe.get_all(
            "Bank Account",
            filters={"company": company, "is_company_account": 1},
            fields=["name", "account_name", "account", "bank", "bank_account_no", "branch_code", "ifsc_code"]
        )
        for ba in bank_accts:
            bank_doc = frappe.get_doc("Bank", ba.bank) if ba.bank else None
            ba.bank_name = bank_doc.bank_name if bank_doc else ""
            ba.ifsc_code = ba.ifsc_code or getattr(bank_doc, "ifsc_code", "") or ""
            ba.branch_code = ba.branch_code or ""

        context.bank_accounts = bank_accts
        context.company_currency = frappe.get_value("Company", company, "default_currency") or "INR"

    return context
