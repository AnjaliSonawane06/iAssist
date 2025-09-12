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
    attachments = data.pop("attachments",[])
    if not docname:
        return {
            "status_code": 400,
            "message": "Missing required field to update on IAssist:'name'",
            "data": {}
        }

    if not frappe.db.exists(refer_doctype, docname):
        return {
            "status_code": 404,
            "message": f"{refer_doctype} {docname} does not exist on IAssist.",
            "data": {}
        }

    try:
        doc = frappe.get_doc(refer_doctype, docname)
        valid_fields.pop('custom_referred_doctype')
        assigned_users = data.get("assignees_list", "not_provided")
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
        
        doc.db_set("custom_sync_status", "Synced")
        if assigned_users != "not_provided": 
            if not assigned_users: 
                doc.db_set("custom_assigned_in_icentral", "")
            else:
                assigned_users_html = build_assigned_users_table(assigned_users)
                doc.db_set("custom_assigned_in_icentral", assigned_users_html)
        if attachments:
            save_attachments_for_doc(doc,attachments)
        return {
            "status_code": 200,
            "message": f"{refer_doctype} {docname} updated successfully.",
            "data": doc.as_dict()
        }

    except Exception as e:
        return {
            "status_code": 500,
            "message": f"Error updating document on IAssist {str(e)}",
            "data": {}
        }
def build_assigned_users_table(assigned_users):

    if not assigned_users:
        return "" 

    rows = "".join(f"<tr><td>{i+1}</td><td>{user}</td></tr>" for i, user in enumerate(assigned_users))
    
    table_html = (
        '<table class="table table-bordered small">'
        '<thead><tr><th>Sr No</th><th>Assigned To</th></tr></thead>'
        f'<tbody>{rows}</tbody>'
        '</table>'
    )
    
    return table_html
