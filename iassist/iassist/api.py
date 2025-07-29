import frappe
import json
from frappe import _
from frappe.model.meta import get_meta
import requests
from frappe.utils.password import get_decrypted_password


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

@frappe.whitelist()
def delete_issue(data=None):
    if frappe.request.method != "DELETE":
        frappe.response["http_status_code"] = 405
        return {
            "status_code": 405,
            "msg": "Method Not Allowed. Please use POST.",
            "data": {}
        }

    user = frappe.session.user

    if not frappe.has_permission("Issue", "delete", user=user):
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
    if data.get("name"):
        if frappe.db.exists("Issue",{'name':data.get("name")}):
            doc= frappe.get_doc("Issue",data.get("name"))
            doc.delete()
            return {
                "status_code": 200,
                "msg": f"Issue {data.get('name')} deleted successfully.",
                "data": {}
            }
        else:
            return {
                "status_code": 404,
                "msg": f"Issue {data.get('name')} doc does not exist",
                "data": {}
            }

@frappe.whitelist()
def delete_hdticket(data=None):
    if frappe.request.method != "DELETE":
        frappe.response["http_status_code"] = 405
        return {
            "status_code": 405,
            "msg": "Method Not Allowed. Please use POST.",
            "data": {}
        }

    user = frappe.session.user

    if not frappe.has_permission("HD Ticket", "delete", user=user):
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
    if data.get("name"):
        if frappe.db.exists("HD Ticket",{'name':data.get("name")}):
            doc= frappe.get_doc("HD Ticket",data.get("name"))
            doc.delete()
            return {
                "status_code": 200,
                "msg": f"HD Ticket {data.get('name')} deleted successfully.",
                "data": {}
            }
        else:
            return {
                "status_code": 404,
                "msg": f"HD Ticket {data.get('name')} doc does not exist",
                "data": {}
            }
        
def map_valid_fields(doctype, data):
    meta = get_meta(doctype)
    valid_fieldnames = [df.fieldname for df in meta.fields] + ["name"]
    return {key: value for key, value in data.items() if key in valid_fieldnames}


def sync_to_central_support(doc, method):
    try:
        config = frappe.get_single("IAssist Support Configurations")

        if not config.is_active or getattr(doc, "synced_from_remote", 0):
            return

        base_url = config.central_support_url.rstrip("/")
        token_url = f"{base_url}/api/method/icentral_support.icentral_support.api.issue.generate_token"
        doctype = doc.doctype
        endpoint_path = get_create_url(doctype)
        if not endpoint_path:
            frappe.logger().error(f"No endpoint defined for Doctype: {doctype}")
            return

        create_url = f"{base_url}{endpoint_path}"
        data_login = {"username": config.username, "password": config.get_password("password")}
        auth_response = requests.post(token_url, json=data_login) 
        
        if auth_response.status_code == 200:
            auth_data = auth_response.json()
            api_key = auth_data["message"]["api_key"]
            api_secret = auth_data["message"]["api_secret"]

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


def get_doc_payload(doctype, doc):
    meta = get_meta(doctype)
    valid_fieldnames = [df.fieldname for df in meta.fields] + ["name", "doctype"]

    doc_dict = doc if isinstance(doc, dict) else doc.as_dict()

    return {key: value for key, value in doc_dict.items() if key in valid_fieldnames}


def get_create_url(doctype):
    if not doctype:
        return
    url=""
    if doctype=="Issue":
        url = "/api/method/icentral_support.icentral_support.api.issue.create_issue"
    elif doctype=="HD Ticket":
        url = "/api/method/icentral_support.icentral_support.api.hd_ticket.create_hd_ticket"
    return url




@frappe.whitelist()
def delete_hdticket(data=None):
    if frappe.request.method != "DELETE":
        frappe.response["http_status_code"] = 405
        return {
            "status_code": 405,
            "msg": "Method Not Allowed. Please use POST.",
            "data": {}
        }

    user = frappe.session.user

    if not frappe.has_permission("HD Ticket", "delete", user=user):
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
    if data.get("name"):
        if frappe.db.exists("HD Ticket",{'name':data.get("name")}):
            doc= frappe.get_doc("HD Ticket",data.get("name"))
            doc.delete()
            return {
                "status_code": 200,
                "msg": f"HD Ticket {data.get('name')} deleted successfully.",
                "data": {}
            }
        else:
            return {
                "status_code": 404,
                "msg": f"HD Ticket {data.get('name')} doc does not exist",
                "data": {}
            }
        
def map_valid_fields(doctype, data):
    meta = get_meta(doctype)
    valid_fieldnames = [df.fieldname for df in meta.fields] + ["name"]
    return {key: value for key, value in data.items() if key in valid_fieldnames}


def sync_to_central_support_to_update(doc, method):
    try:
        config = frappe.get_single("IAssist Support Configurations")

        if not config.is_active or getattr(doc, "synced_from_remote", 0):
            return

        base_url = config.central_support_url.rstrip("/")
        token_url = f"{base_url}/api/method/icentral_support.icentral_support.api.issue.generate_token"
        doctype = config.doctype
        endpoint_path = get_update_url(doctype)
        if not endpoint_path:
            frappe.logger().error(f"No endpoint defined for Doctype: {doctype}")
            return

        create_url = f"{base_url}{endpoint_path}"
        data_login = {"username": config.username, "password": config.get_password("password")}
        auth_response = requests.post(token_url, json=data_login) 
        
        if auth_response.status_code == 200:
            auth_data = auth_response.json()
            api_key = auth_data["message"]["api_key"]
            api_secret = auth_data["message"]["api_secret"]

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
        user_doc.api_key = frappe.generate_hash(length=15)
        user_doc.api_secret = frappe.generate_hash(length=15)
        user_doc.save(ignore_permissions=True)
        
        return {
        "status": 200,
        "api_key": user_doc.api_key,
        "api_secret": user_doc.get_password("api_secret")
        }

    return {"status": 401, "message": "Invalid login"}

