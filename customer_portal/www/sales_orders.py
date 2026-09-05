import frappe
from frappe.utils import formatdate
from .get_base_context import get_base_context

def get_context(context):
    context = get_base_context(context)
    context.title = "Sales Orders"

    # Filters
    search_q = frappe.form_dict.get("search", "")
    status_filter = frappe.form_dict.get("status", "")
    time_filter = frappe.form_dict.get("time", "")
    date_filter = frappe.form_dict.get("date", "")
    
    try:
        limit = int(frappe.form_dict.get("limit", 50))
    except (ValueError, TypeError):
        limit = 50

    filters = {"customer": context.customer_id, "docstatus": ("!=", 2)}
    if status_filter and status_filter != "All Statuses":
        filters["status"] = status_filter

    from frappe.utils import add_months, get_first_day, get_last_day, today
    if date_filter:
        filters["transaction_date"] = date_filter
    elif time_filter:
        if time_filter == "this_month":
            filters["transaction_date"] = ["between", [get_first_day(today()), get_last_day(today())]]
        elif time_filter == "last_3_months":
            filters["transaction_date"] = ["between", [get_first_day(add_months(today(), -3)), get_last_day(today())]]
        elif time_filter == "this_year":
            from datetime import datetime
            current_year = datetime.now().year
            filters["transaction_date"] = ["between", [f"{current_year}-01-01", f"{current_year}-12-31"]]

    context.limit = limit
    context.has_more = False

    # Fetch Sales Orders
    if search_q:
        orders = frappe.get_all(
            "Sales Order",
            filters=filters,
            or_filters=[
                ["name", "like", f"%{search_q}%"],
                ["po_no", "like", f"%{search_q}%"]
            ],
            fields=["name", "transaction_date", "status", "grand_total", "currency"],
            order_by="transaction_date desc",
            limit=limit + 1
        )
    else:
        orders = frappe.get_all(
            "Sales Order",
            filters=filters,
            fields=["name", "transaction_date", "status", "grand_total", "currency"],
            order_by="transaction_date desc",
            limit=limit + 1
        )
        
    if len(orders) > limit:
        context.has_more = True
        orders = orders[:limit]

    for order in orders:
        order.formatted_date = formatdate(order.transaction_date, "dd MMM yyyy")
        
        # count items
        items_count = frappe.db.count("Sales Order Item", {"parent": order.name})
        order.items_count = items_count

        # fetch related invoice
        invoice = frappe.db.get_value("Sales Invoice Item", {"sales_order": order.name}, "parent")
        order.invoice_name = invoice if invoice else "—"

        # fetch related delivery
        delivery = frappe.db.get_value("Delivery Note Item", {"against_sales_order": order.name}, "parent")
        order.delivery_name = delivery if delivery else "—"

    context.orders = orders
    return context