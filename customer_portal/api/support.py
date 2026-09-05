import frappe

@frappe.whitelist()
def create_ticket(subject, description, issue_type, reference=""):
    user = frappe.session.user
    if user == "Guest":
        frappe.throw("You must be logged in to create a ticket.")
        
    # Get the contact associated with this user
    contact_name = frappe.db.get_value("Contact", {"user": user}, "name")
    if not contact_name:
        # Check by email ID if user link is missing
        contact_name = frappe.db.get_value("Contact", {"email_id": user}, "name")
        
    customer = None
    if contact_name:
        # Get Customer via Dynamic Link
        customer = frappe.db.get_value("Dynamic Link", 
            {"parent": contact_name, "parenttype": "Contact", "link_doctype": "Customer"}, 
            "link_name"
        )
        
    if not customer:
        customer = frappe.db.get_value("Portal User", {"user": user, "parenttype": "Customer"}, "parent")
    
    if not customer:
        frappe.throw("No customer linked to this user account.")
        
    # Prepare description with reference if provided
    final_description = description
    if reference:
        final_description = f"Reference: {reference}\n\n{description}"
        
    issue = frappe.new_doc("Customer Support Request")
    issue.subject = subject
    issue.description = final_description
    issue.category = issue_type if issue_type else "Other"
    issue.customer = customer
    issue.posting_date = frappe.utils.nowdate()
    # issue.raised_by = user # Custom doctype doesn't have raised_by, Frappe automatically tracks owner
    
    issue.insert(ignore_permissions=True)
    frappe.db.commit()
    
    return issue.name
