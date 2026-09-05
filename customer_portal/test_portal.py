import frappe
from frappe.website.serve import get_response

def run_tests():
    users = frappe.get_all("Contact", fields=["email_id"], filters={"email_id": ["!=", ""]})
    emails = set(u.email_id for u in users if u.email_id)

    for email in emails:
        frappe.session.user = email
        try:
            r = get_response("/portal")
        except frappe.exceptions.Redirect:
            pass
        except Exception as e:
            if "object is not bound" in str(e):
                pass
            else:
                print(f"Error for {email}: {e}")
                import traceback
                traceback.print_exc()
                break
