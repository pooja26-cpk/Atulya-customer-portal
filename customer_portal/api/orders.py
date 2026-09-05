import frappe
from .dashboard import _get_customer

@frappe.whitelist()
def get_orders(status=None, from_date=None, to_date=None):
    cust = _get_customer()

    filters = {"customer": cust, "docstatus": 1}
    if from_date: filters["transaction_date"] = [">=", from_date]
    if to_date:   filters["transaction_date"] = ["<=", to_date]
    if status:    filters["status"] = status

    return frappe.get_all("Sales Order", filters=filters,
        fields=["name", "transaction_date", "status",
                "grand_total", "total_qty"],
        order_by="transaction_date desc", page_length=50)

import json

@frappe.whitelist()
def search_items(query=""):
    _get_customer() # Security check
    filters = {"disabled": 0, "is_sales_item": 1}
    if query:
        filters["item_code"] = ["like", f"%{query}%"]
        
    items = frappe.get_all("Item", filters=filters, fields=["item_code", "item_name"], limit=20)
    if query and not items:
        # Also try by item name
        items = frappe.get_all("Item", filters={"disabled": 0, "is_sales_item": 1, "item_name": ["like", f"%{query}%"]}, fields=["item_code", "item_name"], limit=20)
    return items

@frappe.whitelist()
def get_item_details(item_code):
    cust = _get_customer() # Security check
    item = frappe.get_doc("Item", item_code)
    
    # Get Customer Default Price List
    price_list = frappe.db.get_value("Customer", cust, "default_price_list")
    if not price_list:
        price_list = frappe.db.get_value("Selling Settings", None, "selling_price_list")
        
    rate = 0
    if price_list:
        rate = frappe.db.get_value("Item Price", {"item_code": item_code, "price_list": price_list, "selling": 1}, "price_list_rate") or 0
        
    if not rate:
        # Fallback to any selling price
        rate = frappe.db.get_value("Item Price", {"item_code": item_code, "selling": 1}, "price_list_rate") or 0
        
    if not rate:
        # Fallback to standard rate if available on Item
        rate = getattr(item, "standard_rate", 0)

    return {
        "item_code": item.item_code,
        "description": item.description or item.item_name,
        "uom": item.stock_uom,
        "rate": rate
    }

@frappe.whitelist()
def place_order(order_data, save_draft=0):
    cust = _get_customer() # Security check
    
    if isinstance(order_data, str):
        order_data = json.loads(order_data)
        
    so = frappe.new_doc("Sales Order")
    so.customer = cust
    so.transaction_date = order_data.get("order_date")
    so.delivery_date = order_data.get("expected_delivery")
    so.customer_address = order_data.get("billing_address")
    so.shipping_address_name = order_data.get("shipping_address")
    
    for item in order_data.get("items", []):
        if not item.get("item_code") or not float(item.get("qty", 0)):
            continue
        so.append("items", {
            "item_code": item.get("item_code"),
            "qty": item.get("qty"),
            "uom": item.get("uom"),
            "rate": item.get("rate")
        })
        
    if not so.get("items"):
        frappe.throw("Please add at least one valid item.")
        
    so.insert(ignore_permissions=True)
    
    # Add notes if provided
    notes = order_data.get("notes")
    if notes:
        so.add_comment("Comment", text=notes)
        
    if not int(save_draft):
        so.submit()
        
    return so.name

@frappe.whitelist()
def approve_order(order_name):
    cust = _get_customer()
    
    so = frappe.get_doc("Sales Order", order_name)
    if so.customer != cust:
        frappe.throw("Not Authorized", frappe.PermissionError)
        
    if so.docstatus != 0:
        frappe.throw("Order is not in Pending Approval state")
        
    so.flags.ignore_permissions = True
    so.submit()
    return "Success"
    
@frappe.whitelist()
def reject_order(order_name, reason=""):
    cust = _get_customer()
    
    so = frappe.get_doc("Sales Order", order_name)
    if so.customer != cust:
        frappe.throw("Not Authorized", frappe.PermissionError)
        
    if so.docstatus != 0:
        frappe.throw("Order is not in Pending Approval state")
        
    frappe.delete_doc("Sales Order", order_name, ignore_permissions=True)
    return "Success"
