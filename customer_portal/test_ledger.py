import frappe
from frappe.website.serve import get_response

def execute():
    frappe.set_user("Administrator")
    frappe.local.path = "/ledger"
    frappe.local.request = frappe._dict({"path": "/ledger"})
    
    # Check limit 10
    frappe.local.form_dict = frappe._dict({"limit_len": 10})
    response = get_response("/ledger")
    html_10 = response.get_data().decode()
    count_10 = html_10.count('<tr style="border-bottom: 1px solid')
    
    # Check limit 20
    frappe.local.form_dict = frappe._dict({"limit_len": 20})
    response = get_response("/ledger")
    html_20 = response.get_data().decode()
    count_20 = html_20.count('<tr style="border-bottom: 1px solid')
    
    print(f"COUNT 10: {count_10}")
    print(f"COUNT 20: {count_20}")
