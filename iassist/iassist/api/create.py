import frappe
import json
from frappe import _
from iassist.iassist.api.api import map_valid_fields, save_attachments_for_doc


@frappe.whitelist(allow_guest=False)
def create_hdticket(data=None):
    if frappe.request.method != "POST":
        frappe.response["http_status_code"] = 405
        return {
            "status_code": 405,
            "msg": "Method Not Allowed. Please use POST.",
            "data": {}
        }

    try:
        if not data:
            data = frappe.request.data
            data = json.loads(data)

    except Exception:
        raise frappe.ValidationError("Invalid JSON data provided.")

    if not isinstance(data, dict):
        raise frappe.ValidationError("Invalid input format. Expected JSON object.")

    user = frappe.session.user
    if not frappe.has_permission("HD Ticket", "create", user=user):
        raise frappe.PermissionError("You do not have permission to create an Issue.")
    attachments = data.pop("attachments", [])
    required_fields = ["subject"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        raise frappe.ValidationError(f"Missing required fields: {', '.join(missing)}")

    valid_data = map_valid_fields("HD Ticket", data)

    doc = frappe.new_doc("HD Ticket")
    for key, value in valid_data.items():
        if key!= 'name':
            setattr(doc, key, value)

    doc.save()
    save_attachments_for_doc(doc, attachments)
    return {
        "status_code": 200,
        "message": "HD Ticket created successfully",
        "data": {"name": doc.name}
    }


@frappe.whitelist()
def create_issue(data=None):
    if frappe.request.method != "POST":
        frappe.response["http_status_code"] = 405
        return {
            "status_code": 405,
            "msg": "Method Not Allowed. Please use POST.",
            "data": {}
        }

    try:
        if not data:
            data = frappe.request.data
            data = json.loads(data)
    except Exception:
        raise frappe.ValidationError("Invalid JSON data provided.")

    if not isinstance(data, dict):
        raise frappe.ValidationError("Invalid input format. Expected JSON object.")

    user = frappe.session.user
    if not frappe.has_permission("Issue", "create", user=user):
        raise frappe.PermissionError("You do not have permission to create an Issue.")
    
    attachments = data.pop("attachments", [])
    required_fields = ["subject"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        raise frappe.ValidationError(f"Missing required fields: {', '.join(missing)}")

    valid_data = map_valid_fields("Issue", data)

    doc = frappe.new_doc("Issue")
    for key, value in valid_data.items():
        if key!= 'name':
            setattr(doc, key, value)

    doc.save(ignore_permissions=True)
    save_attachments_for_doc(doc, attachments)
    return {
        "status_code": 200,
        "message": "Issue created successfully",
        "data": {"name": doc.name}
    }

