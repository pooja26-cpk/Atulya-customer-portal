import frappe

def set_customer_on_issue(doc, method):
    # Resolve customer from logged-in user - never from the form
    user = frappe.session.user
    contact = frappe.db.get_value("Contact", {"email_id": user}, "name")
    customer = frappe.db.get_value("Dynamic Link", 
        {"parent": contact, "parenttype": "Contact", "link_doctype": "Customer"}, 
        "link_name"
    ) if contact else None
    
    if not customer:
        customer = frappe.db.get_value("Portal User", {"user": user, "parenttype": "Customer"}, "parent")
    
    if customer:
        doc.customer = customer
        doc.raised_by = user
        doc.status = "Open"

def update_website_context(context):
    """Inject customer context into all portal pages so the sidebar always has it"""
    user = frappe.session.user
    if user == "Guest":
        return context
        
    context["user_name"] = frappe.db.get_value("User", user, "full_name") or user
    
    # Fetch Customer Link
    contact = frappe.db.get_value("Contact", {"email_id": user}, "name")
    cust = None
    if contact:
        cust = frappe.db.get_value("Dynamic Link", 
            {"parent": contact, "parenttype": "Contact", "link_doctype": "Customer"}, 
            "link_name"
        )
    
    if not cust:
        cust = frappe.db.get_value("Portal User", {"user": user, "parenttype": "Customer"}, "parent")
        
    if cust:
        context["customer_id"] = cust

        # Inject sidebar counts so the base template can show badges
        try:
            # Pending Sales Orders (posted orders not completed/delivered)
            pending_sql = """
                SELECT COUNT(*) FROM `tabSales Order`
                WHERE customer = %s AND docstatus = 1
                  AND status NOT IN ('Completed', 'Delivered')
            """
            context["pending_orders_count"] = frappe.db.sql(pending_sql, cust)[0][0] or 0

            # Overdue invoices (posted, outstanding > 0, due_date < today)
            today = frappe.utils.nowdate()
            overdue_sql = """
                SELECT COUNT(*) FROM `tabSales Invoice`
                WHERE customer = %s AND docstatus = 1
                  AND outstanding_amount > 0 AND due_date < %s
            """
            context["overdue_count"] = frappe.db.sql(overdue_sql, (cust, today))[0][0] or 0

            # Unread notifications for this user (Notification Log has 'read' check)
            notif_sql = """
                SELECT COUNT(*) FROM `tabNotification Log`
                WHERE for_user = %s AND `read` = 0
            """
            try:
                context["unread_notifications_count"] = frappe.db.sql(notif_sql, user)[0][0] or 0
            except Exception:
                # Older/newer systems may have different notification models
                context["unread_notifications_count"] = 0
        except Exception:
            context.setdefault("pending_orders_count", 0)
            context.setdefault("overdue_count", 0)
            context.setdefault("unread_notifications_count", 0)
    return context
