import frappe
import json
from frappe import _
from frappe.model.meta import get_meta


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


@frappe.whitelist(allow_guest=False)
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

