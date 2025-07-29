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


def sync_to_central_support_to_update(doc, method):
    try:
        config = frappe.get_single("IAssist Support Configurations")

        if not config.is_active or getattr(doc, "synced_from_remote", 0):
            return

        base_url = config.central_support_url.rstrip("/")
        doctype = config.doctype
        endpoint_path = get_update_url(doctype)
        if not endpoint_path:
            frappe.logger().error(f"No endpoint defined for Doctype: {doctype}")
            return

        create_url = f"{base_url}{endpoint_path}"
      
        api_key = config.api_key
        api_secret = config.get_password("api_secret")
        if not api_key or not api_secret:
            return

        headers = {
            "Authorization": f"token {api_key}:{api_secret}",
            "Content-Type": "application/json",
            "Expect": ""
        }

        payload = get_doc_payload(doctype, doc)
        
        response = requests.post(create_url,json= payload, headers=headers)
        
        if response.status_code == 200:
            return {"msg": "Issue synced successfully", "data": doc.name}
        else:
            frappe.logger().error(f"Central sync failed [{response.status_code}]: {response.text}")

    except Exception:
        frappe.logger().error(f"Error during sync to central: {frappe.get_traceback()}")

