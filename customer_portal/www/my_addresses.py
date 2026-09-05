import frappe
from .get_base_context import get_base_context

def get_context(context):
    context = get_base_context(context)
    context.title = "Addresses"
    context.pathname = "/addresses"
    return context