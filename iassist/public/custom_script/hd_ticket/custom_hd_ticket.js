frappe.ui.form.on("HD Ticket", {
    refresh: function(frm) {
        frappe.call({
            method: "iassist.iassist.api.api.get_allowed_user",
            args: { doctype: "IAssist Support Configurations" },
            callback: function(r) {
                if (r.message && r.message == 1) {
                    
                    if (!frm.doc.custom_sync_status) {
                        frm.add_custom_button("Sync to Central Support", function () {
                            frappe.call({
                                method: "iassist.iassist.api.api.sync_to_create",
                                args: {
                                    docname: frm.doc.name,
                                    doctype: frm.doc.doctype
                                },
                                callback: function (res) {
                                    if (!res.exc) {
                                        frappe.msgprint("Ticket synced successfully!");
                                        frm.reload_doc();
                                    }
                                }
                            });
                        });
                    } 
                    else {
                        frm.add_custom_button("Update to Central Support", function () {
                            frappe.call({
                                method: "iassist.iassist.api.api.sync_to_update",
                                args: {
                                    docname: frm.doc.name,
                                    doctype: frm.doc.doctype
                                },
                                callback: function (res) {
                                    if (!res.exc) {
                                        frappe.msgprint("Ticket updated successfully!");
                                        frm.reload_doc();
                                    }
                                }
                            });
                        });
                    }
                }
            }
        });
    }
});
