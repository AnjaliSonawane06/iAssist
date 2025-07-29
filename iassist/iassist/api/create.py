import frappe
import json
from frappe import _
from frappe.model.meta import get_meta
import requests
from frappe.utils.password import get_decrypted_password
from iassist.iassist.api.api import *


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

    return {
        "status_code": 200,
        "message": "Issue created successfully",
        "data": {"name": doc.name}
    }


def sync_to_central_support(doc, method):
    try:
        config = frappe.get_single("IAssist Support Configurations")

        if not config.is_active or getattr(doc, "synced_from_remote", 0):
            return

        base_url = config.central_support_url.rstrip("/")
        doctype = doc.doctype
        endpoint_path = get_create_url(doctype)
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
        if doctype == "Issue":
            payload["custom_iassist_issue_id"]= doc.name
        elif doctype == "HD Ticket":
            payload["custom_hd_ticket_id"] = doc.name

        payload["synced_from_remote"] = 1
        payload["custom_url"] = frappe.utils.get_url()
        
        response = requests.post(create_url,json= payload, headers=headers)
        response_data = response.json()  
        doc.custom_last_sync = frappe.utils.get_datetime()
        print(response_data)    
        name = response_data['message']['data']['name']
        if doctype == "Issue":
            doc.custom_master_ic_id = name
        elif doctype=="HD Ticket":
            doc.custom_master_ic_id = name

        if response.status_code == 200:
            return {"msg": "Issue synced successfully", "data": doc.name}
        else:
            frappe.logger().error(f"Central sync failed [{response.status_code}]: {response.text}")

    except Exception:
        frappe.logger().error(f"Error during sync to central: {frappe.get_traceback()}")

