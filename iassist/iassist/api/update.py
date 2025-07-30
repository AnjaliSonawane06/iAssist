import frappe
import json
from frappe import _
from frappe.model.meta import get_meta
import requests
from frappe.utils.password import get_decrypted_password
from iassist.iassist.api.api import *


@frappe.whitelist()
def update_hdticket(data=None):
    if frappe.request.method != "POST":
        frappe.response["http_status_code"] = 405
        return {
            "status_code": 405,
            "msg": "Method Not Allowed. Please use POST.",
            "data": {}
        }

    user = frappe.session.user

    if not frappe.has_permission("HD Ticket", "write", user=user):
        raise frappe.PermissionError(_("You do not have permission to update this document."))

    try:
        if not data:
            data = frappe.request.data
            data = json.loads(data)
    except Exception as e:
        return {
            "status_code": 400,
            "msg": f"Invalid request data: {str(e)}",
            "data": {}
        }

    valid_fields = map_valid_fields("HD Ticket", data)
    docname = valid_fields.get("name")

    if not docname:
        return {
            "status_code": 400,
            "msg": "Missing required field: 'name'",
            "data": {}
        }

    if not frappe.db.exists("HD Ticket", docname):
        return {
            "status_code": 404,
            "msg": f"HD Ticket {docname} does not exist.",
            "data": {}
        }

    try:
        doc = frappe.get_doc("HD Ticket", docname)
        for key, value in valid_fields.items():
            if key != "name":
                setattr(doc, key, value)
        doc.save()

        return {
            "status_code": 200,
            "msg": f"HD Ticket {docname} updated successfully.",
            "data": doc.as_dict()
        }

    except Exception as e:
        return {
            "status_code": 500,
            "msg": f"Error updating document: {str(e)}",
            "data": {}
        }


@frappe.whitelist()
def update_issue(data=None):
    if frappe.request.method != "POST":
        frappe.response["http_status_code"] = 405
        return {
            "status_code": 405,
            "msg": "Method Not Allowed. Please use POST.",
            "data": {}
        }

    user = frappe.session.user

    if not frappe.has_permission("Issue", "write", user=user):
        raise frappe.PermissionError(_("You do not have permission to update this document."))

    try:
        if not data:
            data = frappe.request.data
            data = json.loads(data)
    except Exception as e:
        return {
            "status_code": 400,
            "msg": f"Invalid request data: {str(e)}",
            "data": {}
        }

    valid_fields = map_valid_fields("Issue", data)
    docname = valid_fields.get("name")

    if not docname:
        return {
            "status_code": 400,
            "msg": "Missing required field: 'name'",
            "data": {}
        }

    if not frappe.db.exists("Issue", docname):
        return {
            "status_code": 404,
            "msg": f"Issue {docname} does not exist.",
            "data": {}
        }

    try:
        doc = frappe.get_doc("Issue", docname)
        for key, value in valid_fields.items():
            if key != "name":
                setattr(doc, key, value)
        doc.save()

        return {
            "status_code": 200,
            "msg": f"Issue {docname} updated successfully.",
            "data": doc.as_dict()
        }

    except Exception as e:
        return {
            "status_code": 500,
            "msg": f"Error updating document: {str(e)}",
            "data": {}
        }

