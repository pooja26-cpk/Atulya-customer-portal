import frappe
from .dashboard import _get_customer

@frappe.whitelist()
def get_ledger(from_date=None, to_date=None):
    cust = _get_customer()

    filters = {"party_type": "Customer", "party": cust, "is_cancelled": 0}
    if from_date: filters["posting_date"] = [">=", from_date]
    if to_date:   filters["posting_date"] = ["<=", to_date]

    return frappe.get_all("GL Entry", filters=filters,
        fields=["name", "posting_date", "account",
                "debit", "credit", "voucher_no"],
        order_by="posting_date desc", page_length=50)
