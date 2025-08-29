import frappe
from frappe import _
from frappe.model.meta import get_meta
import requests
import base64
from frappe.utils.file_manager import save_file
import datetime
import uuid
import json

def map_valid_fields(doctype, data):
    meta = get_meta(doctype)
    valid_fieldnames = [df.fieldname for df in meta.fields] + ["name"]
    return {key: value for key, value in data.items() if key in valid_fieldnames}

def get_doc_payload(doctype, doc):
    meta = get_meta(doctype)
    valid_fieldnames = [df.fieldname for df in meta.fields] + ["name", "doctype"]
    
    exclude_fields = {"contact", "company"}  
    valid_fieldnames = [field for field in valid_fieldnames if field not in exclude_fields]

    doc_dict = doc if isinstance(doc, dict) else doc.as_dict()

    return {
        key: safe_json_value(value)
        for key, value in doc_dict.items()
        if key in valid_fieldnames
    }

def safe_json_value(value):
    import datetime, uuid

    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.isoformat()
    if isinstance(value, datetime.timedelta):
        # convert timedelta to HH:MM:SS string
        return str(value)
    if isinstance(value, uuid.UUID):
        return str(value)
    return value


def get_create_url(doctype):
    if not doctype:
        return
    url = "/api/method/icentral_support.icentral_support.api.issue.create_issue"
    return url


def get_update_url(doctype):
    if not doctype:
        return
    url = "/api/method/icentral_support.icentral_support.api.issue.update_issue"
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
    if not config.is_active:
        return
    base_url = config.central_support_url.rstrip("/")
    token_url = f"{base_url}/api/method/icentral_support.icentral_support.api.issue.generate_token"
    
    if config.is_multiple_users:
        for user_row in config.ics_multi_user_details:
            data_login = {"username": user_row.username, "password": user_row.get_password("password")}
            auth_response = requests.post(token_url, json=data_login) 
    
            if auth_response.status_code == 200:
                auth_data = auth_response.json()
                api_key = auth_data["message"]["api_key"]
                api_secret = auth_data["message"]["api_secret"]
                user_row.api_key = api_key
                user_row.api_secret= api_secret
    else:
        data_login = {"username": config.username, "password": config.get_password("password")}
        auth_response = requests.post(token_url, json=data_login) 
        if auth_response.status_code == 200:
            auth_data = auth_response.json()
            api_key = auth_data["message"]["api_key"]
            api_secret = auth_data["message"]["api_secret"]
            config.api_key = api_key
            config.api_secret = api_secret
    config.save()

def handle_attachments_in_payload(payload):
    for field, value in payload.items():
        if isinstance(value, str):
            matches = re.findall(r'src="([^"]+)"', value)
            for match in matches:
                if match.startswith("/private/files/") or match.startswith("/files/"):
                    b64 = file_to_base64(match)
                    if b64:
                        value = value.replace(match, f"data:image/png;base64,{b64}")
            payload[field] = value
            if value.startswith("/private/files/") or value.startswith("/files/"):
                b64 = file_to_base64(value)
                if b64:
                    payload[field] = b64
    return payload


def file_to_base64(file_url):
    try:
        clean_url = file_url.split("?")[0]

        file_path = frappe.get_site_path(clean_url.lstrip("/"))

        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    except Exception as e:
        frappe.log_error(
            title="Attachment Encoding Failed",
            message=f"File: {file_url}, Error: {str(e)}"
        )
        return None

def get_updated_payload(doc):
    last_sync = doc.custom_last_sync
    changed_fields = {}

    if not last_sync:
        for field in doc.meta.fields:
            if field.fieldname == "referred_doctype":
                continue
            changed_fields[field.fieldname] = safe_json_value(doc.get(field.fieldname))
    else:
        
        history = frappe.db.get_all("Version",
            filters={
                "ref_doctype": doc.doctype,
                "docname": doc.name,
                "modified": [">", last_sync]
            },
            fields=["data"]
        )

        if history:
            for h in history:
                data = frappe.parse_json(h.data)
                if data.get("changed"):
                    for fieldname, old_val, new_val in data["changed"]:
                        changed_fields[fieldname] = safe_json_value(new_val)

    if doc.doctype == "Issue":
        changed_fields["name"] = doc.custom_master_ic_id
    elif doc.doctype == "HD Ticket":
        changed_fields["name"] = doc.custom_master_ticket_id
    elif doc.doctype == "IA Support Tickets":
        changed_fields["name"] = doc.central_ticket_id

    changed_fields["custom_last_sync"] = frappe.utils.now()
    if any("/files/" in str(v) for v in changed_fields.values()):
        changed_fields = handle_attachments_in_payload(changed_fields)

    return changed_fields

# def on_update(doc,method):
#     if getattr(doc.flags,"from_insert",True):
#         return
#     sync_to_central_support_to_update(doc,method)

# def after_insert(doc, method):
#     doc.flags.from_insert = True
#     sync_to_central_support_to_create(doc, method)


def sync_to_central_support_to_create(doc):
    try:
        if check_if_sync_id_exists(doc):
            return
        config = frappe.get_single("IAssist Support Configurations")
        if get_configurations(doc):
            headers = get_configurations(doc)
        else:
            frappe.db.set_value(doc.doctype,doc.name,"custom_sync_status","Not Synced")
            frappe.msgprint("Central sync failed : User is not available in configurations")
            frappe.logger().error("Central sync failed : User is not available in configurations")
 
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
            
        payload["custom_url"] = frappe.utils.get_url()
        payload["custom_referred_doctype"] = doc.doctype
        payload["custom_sync_status"] = "Synced"
        response = requests.post(create_url, json=payload, headers=headers)
        response_data = response.json()
        doc.custom_last_sync = frappe.utils.now()
        if response.status_code == 200:
            referred_doctype = response_data['message']['data']['doctype']
            frappe.db.set_value(doc.doctype, doc.name, {
                    "custom_sync_status": "Synced",
                    "custom_referred_doctype":referred_doctype,
                    "custom_last_sync": frappe.utils.now()
                })
            name = response_data['message']['data']['name']
            if doctype == "Issue":
                frappe.db.set_value(doc.doctype,doc.name,"custom_master_ic_id",name)
            elif doctype == "HD Ticket":
                frappe.db.set_value(doc.doctype,doc.name,"custom_master_ticket_id",name)
            elif doctype == "IA Support Tickets":
                frappe.db.set_value(doc.doctype,doc.name,"central_ticket_id",name)

            return {"message": "Issue synced successfully", "data": doc.name}
        else:
            frappe.db.set_value(doc.doctype,doc.name,"custom_sync_status","Not Synced")
            frappe.logger().error(f"Central sync failed [{response.status_code}]: {response.text}")

    except Exception:
        frappe.logger().error(f"Error during sync to central: {frappe.get_traceback()}")


def sync_to_central_support_to_update(doc):
    try:
        config = frappe.get_single("IAssist Support Configurations")
        if get_configurations(doc):
            headers = get_configurations(doc)
        else:
            frappe.db.set_value(doc.doctype,doc.name,"custom_sync_status","Not Synced")
            frappe.msgprint("Central sync failed : User is not available in configurations")
            frappe.logger().error("Central sync failed : User is not available in configurations")
 
        base_url = config.central_support_url.rstrip("/")
        doctype = doc.doctype 
        endpoint_path = get_update_url(doctype)
        if not endpoint_path:
            frappe.logger().error(f"No endpoint defined for Doctype: {doctype}")
            return

        update_url = f"{base_url}{endpoint_path}"
        payload = get_updated_payload(doc)
        payload["custom_url"] = frappe.utils.get_url()
        payload["custom_referred_doctype"] = doc.custom_referred_doctype
        payload["custom_sync_status"] = "Synced"
        attachments = get_attachments_for_payload(doc)
        if attachments:
            payload["attachments"] = attachments

        response = requests.post(update_url, json=payload, headers=headers)
        if response.status_code == 200:
            frappe.db.set_value(doc.doctype, doc.name,"custom_sync_status", "Synced")
            frappe.db.set_value(doc.doctype, doc.name,"custom_last_sync",frappe.utils.now())
            return {"message": "Issue synced successfully", "data": doc.name}
        else:
            frappe.db.set_value(doc.doctype,doc.name,"custom_sync_status","Not Synced")
            frappe.logger().error(f"Central sync failed [{response.status_code}]: {response.text}")

    except Exception:
        frappe.logger().error(f"Error during sync to central: {frappe.get_traceback()}")

def get_configurations(doc):
    config = frappe.get_single("IAssist Support Configurations")
    if not config.is_active:
        return
    if config.is_multiple_users:        
        logged_user = frappe.session.user
        for user_row in config.ics_multi_user_details:
            if logged_user == user_row.username:
                api_key = user_row.api_key
                api_secret = user_row.get_password("api_secret")
    else:
        api_key = config.api_key
        api_secret = config.get_password("api_secret")

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
            if file_info.file_url.startswith("/private"):
                file_path = frappe.get_site_path(file_info.file_url.lstrip("/"))
            else:
                file_path = frappe.get_site_path("public", file_info.file_url.lstrip("/"))
            
            # file_path = frappe.get_site_path("public", file_info.file_url.lstrip("/"))
            with open(file_path, "rb") as f:
                encoded_content = base64.b64encode(f.read()).decode()

                attachments_payload.append({
                    "file_name": file_info.file_name,
                    "file_type": file_info.file_type,
                    "file_base64": encoded_content
                })
        except Exception as e:
            frappe.logger().error(f"Error encoding file {file_info.file_name}: {str(e)}")

    return attachments_payload


def save_attachments_for_doc(doc, attachments):
    site_url = frappe.utils.get_url()
    for file in attachments:
        file_name = file.get("file_nameuser is 6th jiopyredwectg5'
         ")
        file_base64 = file.get("file_base64")

        if not file_name or not file_base64:
            frappe.logger().warning("Attachment skipped due to missing file_name or file_base64.")
            continue

        # try:
        file_doc = save_file(
            fname=file_name,
            content=file_base64,
            dt=doc.doctype,
            dn=doc.name,
            decode=True
        )

        if file_doc.file_url:
            img_tag = f'<p><img src="{site_url}{file_doc.file_url}" /></p>'

            if not doc.description:
                doc.description = img_tag
            else:
                doc.description += img_tag
        # except Exception as e:
        #     frappe.logger().error(f"Failed to save attachment {file_name}: {e}")

    doc.save()
def check_Sync_status_for_issue():
    record_list = frappe.get_all("Issue",['name'])
    for record in record_list:
        if not record.custom_sync_status == "Synced":
            doc = frappe.get_doc("Issue",record.name)
            if not record.custom_master_ic_id:
                sync_to_central_support_to_create(doc,method=None)
            else:
                sync_to_central_support_to_update(doc,method=None)

def check_Sync_status_for_hd_ticket():
    record_list = frappe.get_all("HD Ticket",['name'])
    for record in record_list:
        if not record.custom_sync_status == "Synced":
            doc = frappe.get_doc("HD Ticket",record.name)
            if not record.custom_master_ticket_id:
                sync_to_central_support_to_create(doc,method=None)
            else:
                sync_to_central_support_to_update(doc,method=None)

def check_if_sync_id_exists(doc):
    if doc.doctype == "Issue" and doc.custom_master_ic_id:
        return
    elif doc.doctype == "IA Support Tickets" and doc.central_ticket_id:
        return
    elif doc.doctype == "HD Ticket" and doc.custom_master_ticket_id:
        return

def sync_comment_to_icentral(doc, method):
    if doc.custom_comment_from_icentral:  
        return
    if doc.reference_doctype not in ("Issue", "IA Support Tickets", "HD Ticket"):
        return

    config = frappe.get_single("IAssist Support Configurations")
    headers = get_configurations(doc)  
    if not headers:
        frappe.db.set_value(doc.doctype, doc.name, "custom_sync_status", "Not Synced")
        frappe.logger().error("Central sync failed : User not available in configurations")
        return

    base_url = config.central_support_url.rstrip("/")
    endpoint_path = f"{base_url}/api/method/icentral_support.icentral_support.api.sync_to_iassist.create_comment_in_icentral"

    reference_name = None
    if doc.reference_doctype == "IA Support Tickets":
        reference_name = frappe.db.get_value(doc.reference_doctype, doc.reference_name, "central_ticket_id")
    elif doc.reference_doctype == "Issue":
        reference_name = frappe.db.get_value(doc.reference_doctype, doc.reference_name, "custom_master_ic_id")
    elif doc.reference_doctype == "HD Ticket":
        reference_name = frappe.db.get_value(doc.reference_doctype, doc.reference_name, "custom_master_ticket_id")

    referred_doctype = frappe.db.get_value(doc.reference_doctype, doc.reference_name, "custom_referred_doctype")
    if not reference_name and referred_doctype:
        return
    payload = get_doc_payload(doc.doctype, doc)
    payload["reference_doctype"] = referred_doctype
    payload["reference_name"] = reference_name
    payload["custom_ia_comment_id"] = doc.name
    payload["custom_comment_from_iassist"] = 1
    payload["custom_ia_comment_id"] = doc.name

    response = requests.post(endpoint_path, json=payload, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        comment_id = response_data["message"]["data"]["name"]
        frappe.db.set_value("Comment", doc.name, "custom_ic_comment_id",comment_id)
        return {"message":"commented successfully"}

def update_comment_in_icentral(doc,method):
    if not doc or doc.is_new():
        return
    if not (doc.reference_doctype == "Issue" or doc.reference_doctype == "IA Support Tickets" or doc.reference_doctype == "HD Ticket"):
        return
    config = frappe.get_single("IAssist Support Configurations")
    if get_configurations(doc):
        headers = get_configurations(doc)
    else:
        frappe.db.set_value(doc.doctype,doc.name,"custom_sync_status","Not Synced")
        frappe.msgprint("Central sync failed : User is not available in configurations")
        frappe.logger().error("Central sync failed : User is not available in configurations")

    base_url = config.central_support_url.rstrip("/")
    doctype = doc.doctype
    endpoint_path = f"{base_url}/api/method/icentral_support.icentral_support.api.sync_to_iassist.update_comment_in_icentral"
    payload = {"name":doc.custom_ic_comment_id, "content":doc.content}

    if not endpoint_path:
        frappe.logger().error(f"No endpoint defined for Doctype: {doctype}")
        return
    response = requests.post(endpoint_path, json=payload, headers=headers)
    if response.status_code == 200:
        return {"message":"commented successfully","data":doc.custom_ic_comment_id}

@frappe.whitelist()
def sync_to_create(doctype,docname):
    doc = frappe.get_doc(doctype,docname)
    sync_to_central_support_to_create(doc)

@frappe.whitelist()
def sync_to_update(docname, doctype):
    doc = frappe.get_doc(doctype,docname)
    sync_to_central_support_to_update(doc)
    return {"status": "success"}

@frappe.whitelist()
def get_allowed_user():
    config = frappe.get_single("IAssist Support Configurations")
    is_allowed_user = 0
    if config.is_multiple_users:
        for user_row in config.ics_multi_user_details:
            if frappe.session.user == user_row.username:
                is_allowed_user = 1
                break
    else:
        if config.username == frappe.session.user:
            is_allowed_user = 1
    return is_allowed_user


def on_update(doc,method):
    doc.custom_sync_status = "Not Synced"
