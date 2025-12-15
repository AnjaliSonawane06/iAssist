import frappe

def on_trash(doc,method):
    warning = 'For deleting this synced documents,You need to request on Icentral.Go to Actions -> Request For Deletion. Note: Sync Status should not be Not Synced'
    if doc.custom_requested_to_delete_ticket==0 and doc.custom_deleted_from_icentral_support==0 and doc.custom_master_ic_id:
        frappe.throw(warning)
     
def on_update(doc,method):
    frappe.db.set_value(doc.doctype,doc.name,"custom_sync_status","Not Synced")
