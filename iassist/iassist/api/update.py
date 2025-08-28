import frappe
import json
from frappe import _
from frappe.model.meta import get_meta
import requests
from frappe.utils.password import get_decrypted_password
from iassist.iassist.api.api import *
from frappe.desk.form.utils import update_comment


@frappe.whitelist()
def update_ticket(data=None):
    if frappe.request.method != "POST":
        frappe.response["http_status_code"] = 405
        return {
            "status_code": 405,
            "message": "Method Not Allowed. Please use POST.",
            "data": {}
        }

    user = frappe.session.user
    
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
    
    refer_doctype = data.get("custom_referred_doctype")

    if not frappe.has_permission(refer_doctype, "write", user=user):
        return{"message":"You do not have permission to update this document."}

    
    # refer_doctype = frappe.get_single_value("IAssist Support Configurations","doctype_for_raising_ticket")
    valid_fields = map_valid_fields(refer_doctype, data)
    docname = valid_fields.get("name")

    if not docname:
        return {
            "status_code": 400,
            "message": "Missing required field: 'name'",
            "data": {}
        }

    if not frappe.db.exists(refer_doctype, docname):
        return {
            "status_code": 404,
            "message": f"{refer_doctype} {docname} does not exist.",
            "data": {}
        }

    try:
        doc = frappe.get_doc(refer_doctype, docname)
        # if refer_doctype == "Issue":
        #     valid_fields['custom_master_ic_id'] = docname
        # elif refer_doctype == "IA Support Tickets":
        #     valid_fields['central_ticket_id'] = docname
        # elif refer_doctype == "HD Ticket":
        #     valid_fields['custom_master_ticket_id'] = docname
        
        for key, value in valid_fields.items():
            if key != "name":
                setattr(doc, key, value)
        doc.save(ignore_permissions=True)
        doc.db_set("custom_sync_status", "Synced", update_modified=False)
        return {
            "status_code": 200,
            "message": f"{refer_doctype} {docname} updated successfully.",
            "data": doc.as_dict()
        }

    except Exception as e:
        return {
            "status_code": 500,
            "message": f"Error updating document: {str(e)}",
            "data": {}
        }

# @frappe.whitelist()
# def update_issue(data=None):
#     if frappe.request.method != "POST":
#         frappe.response["http_status_code"] = 405
#         return {
#             "status_code": 405,
#             "message": "Method Not Allowed. Please use POST.",
#             "data": {}
#         }

#     user = frappe.session.user

#     if not frappe.has_permission("Issue", "write", user=user):
#         return{"message":"You do not have permission to update this document."}

#     try:
#         if not data:
#             data = frappe.request.data
#             data = json.loads(data)
#     except Exception as e:
#         return {
#             "status_code": 400,
#             "message": f"Invalid request data: {str(e)}",
#             "data": {}
#         }

#     valid_fields = map_valid_fields("Issue", data)
#     docname = valid_fields.get("name")

#     if not docname:
#         return {
#             "status_code": 400,
#             "message": "Missing required field: 'name'",
#             "data": {}
#         }

#     if not frappe.db.exists("Issue", docname):
#         return {
#             "status_code": 404,
#             "message": f"Issue {docname} does not exist.",
#             "data": {}
#         }

#     try:
#         doc = frappe.get_doc("Issue", docname)
#         for key, value in valid_fields.items():
#             if key != "name":
#                 setattr(doc, key, value)
#         doc.save()

#         return {
#             "status_code": 200,
#             "message": f"Issue {docname} updated successfully.",
#             "data": doc.as_dict()
#         }

#     except Exception as e:
#         return {
#             "status_code": 500,
#             "message": f"Error updating document: {str(e)}",
#             "data": {}
#         }


# @frappe.whitelist()
# def update_comment_in_iassist(data=None):
#     if not data:
#         data = json.loads(frappe.request.data)
    
#     update_comment(name= data.get("name"),content=data.get("content"))
    
#     return {"status_code":200,"data":{"name":data.get("name")}}
