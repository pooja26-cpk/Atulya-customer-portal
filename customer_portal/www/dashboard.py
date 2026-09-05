from .get_base_context import get_base_context

def get_context(context):
    context = get_base_context(context)
    return context



def debug_render():
    frappe.session.user = "rajesh@sharmaenterprises.com"
    from frappe.website.serve import get_response
    try:
        r = get_response("/portal")
        print("Success")
    except Exception as e:
        import traceback
        traceback.print_exc()