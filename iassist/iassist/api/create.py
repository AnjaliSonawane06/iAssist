import frappe
import json
from frappe import _
from iassist.iassist.api.api import map_valid_fields, save_attachments_for_doc
from frappe.desk.form.utils import add_comment



@frappe.whitelist(allow_guest=False)
def create_ticket(data=None):
    if frappe.request.method != "POST":
        frappe.response["http_status_code"] = 405
        return {
            "status_code": 405,
            "message": "Method Not Allowed. Please use POST.",
            "data": {}
        }

    try:
        if not data:
            data = frappe.request.data
            data = json.loads(data)

    except Exception:
        return{"message": "Invalid JSON data provided."}

    if not isinstance(data, dict):
        return{"message": "Invalid input format. Expected JSON object."}

    user = frappe.session.user
    if not frappe.has_permission(refer_doctype, "create", user=user):
        return{"message":"You do not have permission to create an Issue."}
    
    attachments = data.pop("attachments", [])
    required_fields = ["subject"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return{"message":f"Missing required fields: {', '.join(missing)}"}
    refer_doctype = frappe.get_single_value("IAssist Support Configurations","doctype_for_raising_ticket")
    valid_data = map_valid_fields(refer_doctype, data)

    doc = frappe.new_doc(refer_doctype)
    if refer_doctype == "Issue":
        valid_data['custom_master_ic_id'] = data.get("name")
    elif refer_doctype == "IA Support Tickets":
        valid_data['central_ticket_id'] = data.get("name")
    elif refer_doctype == "HD Ticket":
        valid_data['custom_master_ticket_id'] = data.get("name")
    valid_data['custom_referred_doctype'] = data.get("doctype")
    
    for key, value in valid_data.items():
        if key!= 'name':
            setattr(doc, key, value)

    doc.save()
    save_attachments_for_doc(doc, attachments)
    return {
        "status_code": 200,
        "message": f"{refer_doctype} created successfully",
        "data": {"name": doc.name}
    }
# @frappe.whitelist()
# def create_issue(data=None):
#     if frappe.request.method != "POST":
#         frappe.response["http_status_code"] = 405
#         return {
#             "status_code": 405,
#             "message": "Method Not Allowed. Please use POST.",
#             "data": {}
#         }

#     try:
#         if not data:
#             data = frappe.request.data
#             data = json.loads(data)
#     except Exception:
#         return{"message": "Invalid JSON data provided."}

#     if not isinstance(data, dict):
#         return{"message": "Invalid input format. Expected JSON object."}

#     user = frappe.session.user
#     if not frappe.has_permission("Issue", "create", user=user):
#         return{"message":"You do not have permission to create an Issue."}
    
#     attachments = data.pop("attachments", [])
#     required_fields = ["subject"]
#     missing = [f for f in required_fields if f not in data]
#     if missing:
#         return{"message":f"Missing required fields: {', '.join(missing)}"}

#     valid_data = map_valid_fields("Issue", data)

#     doc = frappe.new_doc("Issue")
#     for key, value in valid_data.items():
#         if key!= 'name':
#             setattr(doc, key, value)

#     doc.save(ignore_permissions=True)
#     save_attachments_for_doc(doc, attachments)
#     return {
#         "status_code": 200,
#         "message": "Issue created successfully",
#         "data": {"name": doc.name}
#     }


@frappe.whitelist()   
def create_comment_to_sync_in_iassist(data=None):
    if not data:
        data = json.loads(frappe.request.data)
    if not frappe.db.exists("Comment",{'custom_ic_comment_id':data.get("name")},['name']):
        comment_doc = add_comment(
        reference_doctype=data.get("reference_doctype"),
        reference_name=data.get("reference_name"),
        content=data.get("content"),
        comment_email=data.get("comment_email"),
        comment_by=data.get("comment_by"))
        
        if data.get("name"):
            frappe.db.set_value("Comment",comment_doc.name, "custom_ic_comment_id",  data.get("name"))
        return {"status_code":200,"data":{"name":comment_doc.name}}
   