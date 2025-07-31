import frappe
import json
from frappe import _
from frappe.model.meta import get_meta
import requests
import base64
from frappe.utils.file_manager import save_file
import datetime
import uuid

        
def map_valid_fields(doctype, data):
    meta = get_meta(doctype)
    valid_fieldnames = [df.fieldname for df in meta.fields] + ["name"]
    return {key: value for key, value in data.items() if key in valid_fieldnames}

def get_doc_payload(doctype, doc):
    meta = get_meta(doctype)
    valid_fieldnames = [df.fieldname for df in meta.fields] + ["name", "doctype"]

    doc_dict = doc if isinstance(doc, dict) else doc.as_dict()

    return {
        key: safe_json_value(value)
        for key, value in doc_dict.items()
        if key in valid_fieldnames
    }

def safe_json_value(value):
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.isoformat()
    if isinstance(value, uuid.UUID):
        return str(value)
    return value

def get_create_url(doctype):
    if not doctype:
        return
    url=""
    if doctype=="Issue":
        url = "/api/method/icentral_support.icentral_support.api.issue.create_issue"
    elif doctype=="HD Ticket":
        url = "/api/method/icentral_support.icentral_support.api.hd_ticket.create_hd_ticket"
    return url


def get_update_url(doctype):
    if not doctype:
        return
    url=""
    if doctype=="Issue":
        url = "/api/method/icentral_support.icentral_support.api.issue.update_issue"
    elif doctype=="HD Ticket":
        url = "/api/method/icentral_support.icentral_support.api.hd_ticket.update_hd_ticket"
    return url


@frappe.whitelist(allow_guest=True)
def generate_token(data=None):
    data = frappe.request.get_json()

    username = data.get("username")
    password = data.get("password")
    login_url = f"{frappe.utils.get_url()}/api/method/login"
    response = requests.post(login_url, data={"usr": username, "pwd": password})
    if response.status_code == 200:
        user_doc = frappe.get_doc("User", username)
        if not user_doc.api_key:
            user_doc.api_key = frappe.generate_hash(length=15)
        user_doc.api_secret = frappe.generate_hash(length=15)
        user_doc.save(ignore_permissions=True)
        
        return {
        "status": 200,
        "api_key": user_doc.api_key,
        "api_secret": user_doc.get_password("api_secret")
        }

    return {"status": 401, "message": "Invalid login"}

def set_token_daily():
   
    config = frappe.get_single("IAssist Support Configurations")
    base_url = config.central_support_url.rstrip("/")
    token_url = f"{base_url}/api/method/icentral_support.icentral_support.api.issue.generate_token"
  
    data_login = {"username": config.username, "password": config.get_password("password")}
    auth_response = requests.post(token_url, json=data_login) 
    
    if auth_response.status_code == 200:
        auth_data = auth_response.json()
        api_key = auth_data["message"]["api_key"]
        api_secret = auth_data["message"]["api_secret"]
        config.api_key = api_key
        config.api_secret= api_secret
        config.save()

def get_updated_payload(doc):
    old_doc = frappe.get_doc(doc.doctype, doc.name)

    updated_payload = {}
    for field in doc.meta.fields:
        fieldname = field.fieldname
        if fieldname and hasattr(doc, fieldname):
            old_val = old_doc.get(fieldname)
            new_val = doc.get(fieldname)
            if old_val != new_val:
                updated_payload[fieldname]  = safe_json_value(new_val)

    if not updated_payload:
        frappe.logger().info(f"No changes detected in {doc.doctype} {doc.name}, skipping sync.")
        return
    updated_payload["name"] = doc.name
    if doc.doctype == "Issue":
        updated_payload["name"] = doc.custom_master_ic_id
    elif doc.doctype == "HD Ticket":
        updated_payload["name"] = doc.custom_master_ticket_id
    updated_payload["custom_last_sync"] = frappe.utils.now()
    return updated_payload
   
def before_save(doc, method):
    if doc.is_new():
        sync_to_central_support_to_create(doc, method)
    else:
        sync_to_central_support_to_update(doc, method)


def sync_to_central_support_to_create(doc, method):
    try:
        config = frappe.get_single("IAssist Support Configurations")
        headers = get_configurations(doc)

        base_url = config.central_support_url.rstrip("/")
        doctype = doc.doctype
        endpoint_path = get_create_url(doctype)
        if not endpoint_path:
            frappe.logger().error(f"No endpoint defined for Doctype: {doctype}")
            return

        create_url = f"{base_url}{endpoint_path}"

        payload = get_doc_payload(doctype, doc)
        attachments = get_attachments_for_payload(doc)
        if attachments:
            payload["attachments"] = attachments
        if doctype == "Issue":
            payload["custom_iassist_issue_id"] = doc.name
        elif doctype == "HD Ticket":
            payload["custom_iassist_hd_ticket"] = doc.name

        payload["synced_from_remote"] = 1
        payload["custom_url"] = frappe.utils.get_url()
        
        response = requests.post(create_url, json=payload, headers=headers)
        response_data = response.json()

        doc.custom_last_sync = frappe.utils.now()

        if response.status_code == 200:
            name = response_data['message']['data']['name']
            if doctype == "Issue":
                doc.custom_master_ic_id = name
            elif doctype == "HD Ticket":
                doc.custom_master_ticket_id = name

            return {"message": "Issue synced successfully", "data": doc.name}
        else:
            frappe.logger().error(f"Central sync failed [{response.status_code}]: {response.text}")

    except Exception:
        frappe.logger().error(f"Error during sync to central: {frappe.get_traceback()}")


def sync_to_central_support_to_update(doc, method):
    try:
        config = frappe.get_single("IAssist Support Configurations")

        headers = get_configurations(doc)

        base_url = config.central_support_url.rstrip("/")
        doctype = doc.doctype 
        endpoint_path = get_update_url(doctype)
        if not endpoint_path:
            frappe.logger().error(f"No endpoint defined for Doctype: {doctype}")
            return

        update_url = f"{base_url}{endpoint_path}"
        payload = get_updated_payload(doc)
        attachments = get_attachments_for_payload(doc)
        if attachments:
            payload["attachments"] = attachments

        response = requests.post(update_url, json=payload, headers=headers)
        if response.status_code == 200:
            doc.custom_last_sync = frappe.utils.now()
            return {"message": "Issue synced successfully", "data": doc.name}
        else:
            frappe.logger().error(f"Central sync failed [{response.status_code}]: {response.text}")

    except Exception:
        frappe.logger().error(f"Error during sync to central: {frappe.get_traceback()}")

def get_configurations(doc):
    config = frappe.get_single("IAssist Support Configurations")

    if not config.is_active or getattr(doc, "synced_from_remote", 0):
        return
    api_key = config.api_key
    api_secret = config.get_password("api_secret")
    if not api_key or not api_secret:
        return

    headers = {
        "Authorization": f"token {api_key}:{api_secret}",
        "Content-Type": "application/json",
        "Expect": ""
    }
    return headers

def get_attachments_for_payload(doc):
    attachments_payload = []
    files = frappe.get_all("File", filters={
        "attached_to_doctype": doc.doctype,
        "attached_to_name": doc.name
    }, fields=["file_name", "file_url", "file_type"])

    for file_info in files:
        try:
            file_path = frappe.get_site_path("public", file_info.file_url.lstrip("/"))
            with open(file_path, "rb") as f:
                encoded_content = base64.b64encode(f.read()).decode()

            attachments_payload.append({
                "file_name": file_info.file_name,
                "file_type": file_info.file_type,
                "content_base64": encoded_content
            })

        except Exception as e:
            frappe.logger().error(f"Error encoding file {file_info.file_name}: {str(e)}")

    return attachments_payload


def save_attachments_for_doc(doc, attachments):
    for file in attachments:
        file_name = file.get("file_name")
        file_base64 = file.get("file_base64")

        if not file_name or not file_base64:
            frappe.logger().warning("Attachment skipped due to missing file_name or file_base64.")
            continue
        try:
            save_file(
                fname=file_name,
                content=file_base64,
                dt=doc.doctype,
                dn=doc.name,
                decode=True 
            )
        except Exception as e:
            frappe.logger().error(f"Failed to save attachment {file_name}: {e}")
