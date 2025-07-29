import frappe
import json
from frappe import _
from frappe.model.meta import get_meta
import requests
from frappe.utils.password import get_decrypted_password
from iassist.iassist.api.api import *


@frappe.whitelist(allow_guest=False)
def get_issue(data=None):
    if frappe.request.method != "GET":
        frappe.response["http_status_code"] = 405
        return {
            "status_code": 405,
            "msg": "Method Not Allowed. Please use GET.",
            "data": {}
        }

    user = frappe.session.user

    if not frappe.has_permission("Issue", "read", user=user):
        raise frappe.PermissionError(_("You do not have permission to access this document."))

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
    filters = {key: data.get(key) for key in valid_fields if data.get(key)}

    records = frappe.get_list("Issue", filters=filters, fields="*")

    if not records:
        return {
            "status_code": 200,
            "msg": "No records found.",
            "data": []
        }

    return {
        "status_code": 200,
        "msg": "Data received successfully.",
        "data": records
    }

@frappe.whitelist(allow_guest=False)
def get_hdticket(data=None):
    if frappe.request.method != "GET":
        frappe.response["http_status_code"] = 405
        return {
            "status_code": 405,
            "msg": "Method Not Allowed. Please use GET.",
            "data": {}
        }

    user = frappe.session.user

    if not frappe.has_permission("HD Ticket", "read", user=user):
        raise frappe.PermissionError(_("You do not have permission to access this document."))

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

    fields = ["name", "subject", "status", "customer"]
    filters = {key: data.get(key) for key in fields if data.get(key)}

    records = frappe.get_list("Issue", filters=filters, fields="*")

    if not records:
        return {
            "status_code": 200,
            "msg": "No records found.",
            "data": []
        }

    return {
        "status_code": 200,
        "msg": "Data received successfully.",
        "data": records
    }
