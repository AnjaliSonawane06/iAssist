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
            "message": "Method Not Allowed. Please use GET.",
            "data": {}
        }

    user = frappe.session.user

    if not frappe.has_permission("Issue", "read", user=user):
        return{"message":"You do not have permission to update this document."}

    try:
        if not data:
            data = frappe.request.data
            data = json.loads(data)
    except Exception as e:
        return {
            "status_code": 400,
            "message": f"Invalid request data: {str(e)}",
            "data": {}
        }

    valid_fields = map_valid_fields("Issue", data)
    filters = {key: data.get(key) for key in valid_fields if data.get(key)}

    records = frappe.get_list("Issue", filters=filters, fields="*")

    if not records:
        return {
            "status_code": 200,
            "message": "No records found.",
            "data": []
        }

    return {
        "status_code": 200,
        "message": "Data received successfully.",
        "data": records
    }

@frappe.whitelist(allow_guest=False)
def get_hdticket(data=None):
    if frappe.request.method != "GET":
        frappe.response["http_status_code"] = 405
        return {
            "status_code": 405,
            "message": "Method Not Allowed. Please use GET.",
            "data": {}
        }

    user = frappe.session.user

    if not frappe.has_permission("HD Ticket", "read", user=user):
        return{"message":"You do not have permission to update this document."}

    try:
        if not data:
            data = frappe.request.data
            data = json.loads(data)
    except Exception as e:
        return {
            "status_code": 400,
            "message": f"Invalid request data: {str(e)}",
            "data": {}
        }

    fields = ["name", "subject", "status", "customer"]
    filters = {key: data.get(key) for key in fields if data.get(key)}

    records = frappe.get_list("Issue", filters=filters, fields="*")

    if not records:
        return {
            "status_code": 200,
            "message": "No records found.",
            "data": []
        }

    return {
        "status_code": 200,
        "message": "Data received successfully.",
        "data": records
    }
