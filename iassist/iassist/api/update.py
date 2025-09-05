import frappe
import json
from frappe import _
from iassist.iassist.api.api import *


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
        # attachments = data.pop("attachments", [])
        valid_fields.pop('custom_referred_doctype')
        for key, value in valid_fields.items():
            if key != 'name':
                df = doc.meta.get_field(key)
                if df and df.fieldtype == "Link" and value:
                    if frappe.db.exists(df.options, value):
                        setattr(doc, key, value)
                    else:
                        setattr(doc, key, None) 
                else:
                    setattr(doc, key, value)
                    if key == "status":
                        doc.db_set("status", value)   
        doc.save()
        # save_attachments_for_doc(doc, attachments)
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
