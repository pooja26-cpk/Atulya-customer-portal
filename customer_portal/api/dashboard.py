import frappe
from frappe import _
from frappe.utils import nowdate, flt

def _get_customer():
    """Resolve customer from logged-in user. Never trust browser input."""
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    # Find the Contact linked to this user's email
    contact = frappe.db.get_value("Contact", {"email_id": user}, "name")
    customer = None
    if contact:
        customer = frappe.db.get_value("Dynamic Link", 
            {"parent": contact, "parenttype": "Contact", "link_doctype": "Customer"}, 
            "link_name"
        )

    if not customer:
        customer = frappe.db.get_value("Portal User", {"user": user, "parenttype": "Customer"}, "parent")

    if not customer:
        frappe.throw(_("No customer linked to this account"), frappe.PermissionError)
        
    return customer


@frappe.whitelist()
def get_dashboard_data():
    cust = _get_customer()  # <- security check always first

    # Outstanding + overdue
    inv = frappe.db.sql("""
        SELECT
            SUM(outstanding_amount)                                  AS total_outstanding,
            SUM(CASE WHEN due_date < %s THEN outstanding_amount
                     ELSE 0 END)                                     AS overdue_amount,
            COUNT(*)                                                 AS inv_count,
            SUM(CASE WHEN due_date < %s THEN 1 ELSE 0 END)           AS overdue_count
        FROM `tabSales Invoice`
        WHERE customer = %s AND docstatus = 1
          AND outstanding_amount > 0
    """, (nowdate(), nowdate(), cust), as_dict=True)[0]

    # Credit limit from Customer master
    credit_limit = flt(frappe.db.get_value(
        "Customer Credit Limit",
        {"parent": cust},
        "credit_limit"
    ))

    outstanding   = flt(inv.total_outstanding)
    avail_credit  = max(credit_limit - outstanding, 0)
    util_pct      = (outstanding / credit_limit * 100) if credit_limit else 0

    # Current period sales (this month)
    sales = frappe.db.sql("""
        SELECT SUM(base_grand_total)
        FROM `tabSales Invoice`
        WHERE customer = %s AND docstatus = 1
          AND MONTH(posting_date) = MONTH(CURDATE())
          AND YEAR(posting_date)  = YEAR(CURDATE())
    """, cust)[0][0] or 0

    # Customer ID for sidebar label
    customer_id = frappe.db.get_value("Customer", cust, "name")

    return {
        "customer_id":        customer_id,
        "total_outstanding":  outstanding,
        "overdue_amount":     flt(inv.overdue_amount),
        "credit_limit":       credit_limit,
        "available_credit":   avail_credit,
        "utilisation_pct":    round(util_pct, 2),
        "current_sales":      flt(sales),
        "inv_count":          inv.inv_count or 0,
        "overdue_count":      inv.overdue_count or 0,
    }
