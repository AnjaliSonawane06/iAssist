import frappe
import json
from frappe import _
from frappe.model.meta import get_meta
import requests
from frappe.utils.password import get_decrypted_password
from iassist.iassist.api.api import *



@frappe.whitelist()
def delete_issue(data=None):
    if frappe.request.method != "DELETE":
        frappe.response["http_status_code"] = 405
        return {
            "status_code": 405,
            "message": "Method Not Allowed. Please use POST.",
            "data": {}
        }

    user = frappe.session.user

    if not frappe.has_permission("Issue", "delete", user=user):
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
    if data.get("name"):
        if frappe.db.exists("Issue",{'name':data.get("name")}):
            doc= frappe.get_doc("Issue",data.get("name"))
            doc.delete()
            return {
                "status_code": 200,
                "message": f"Issue {data.get('name')} deleted successfully.",
                "data": {}
            }
        else:
            return {
                "status_code": 404,
                "message": f"Issue {data.get('name')} doc does not exist",
                "data": {}
            }

@frappe.whitelist()
def delete_hdticket(data=None):
    if frappe.request.method != "DELETE":
        frappe.response["http_status_code"] = 405
        return {
            "status_code": 405,
            "message": "Method Not Allowed. Please use POST.",
            "data": {}
        }

    user = frappe.session.user

    if not frappe.has_permission("HD Ticket", "delete", user=user):
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
    if data.get("name"):
        if frappe.db.exists("HD Ticket",{'name':data.get("name")}):
            doc= frappe.get_doc("HD Ticket",data.get("name"))
            doc.delete()
            return {
                "status_code": 200,
                "message": f"HD Ticket {data.get('name')} deleted successfully.",
                "data": {}
            }
        else:
            return {
                "status_code": 404,
                "message": f"HD Ticket {data.get('name')} doc does not exist",
                "data": {}
            }
        