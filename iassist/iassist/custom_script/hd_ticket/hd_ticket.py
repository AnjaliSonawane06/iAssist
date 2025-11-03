import frappe
from frappe.utils import now


def on_trash(doc,method):
    warning = 'For deleting this synced documents,You need to request on Icentral.Go to Actions -> Request For Deletion.' 
    if doc.doctype == "HD Ticket" and doc.custom_master_ticket_id:
        frappe.throw(warning)


def on_update(doc,method):
    frappe.db.set_value(doc.doctype,doc.name,"custom_sync_status","Not Synced")

def validate(doc,method):
    status_wise_activity_table(doc,method)

def status_wise_activity_table(doc,method):

    if frappe.flags.get('ignore_status_activity_flag'):
        return
    
    if doc.is_new():
        activity = {
            "timestamp": now(),
            "status": doc.status,
            "updated_by" : frappe.session.user,
        }
        doc.append("custom_status_wise_activity_table",activity)
    else:
        old_doc = doc.get_doc_before_save()
        if old_doc.status != doc.status:
            activity = {
            "timestamp": now(),
            "status": doc.status,
            "updated_by" : frappe.session.user,
        }
            doc.append("custom_status_wise_activity_table",activity)


