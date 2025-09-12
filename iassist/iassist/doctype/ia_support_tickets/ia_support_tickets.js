// Copyright (c) 2025, New Indictrans Technologies pvt. ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("IA Support Tickets", {
	refresh: function(frm) {
        frappe.call({
            method: "iassist.iassist.api.api.get_allowed_user",
            args: { doctype: "IAssist Support Configurations" },
            callback: function(r) {
                if (r.message && r.message == 1) {
                    
                    if (!frm.doc.central_ticket_id) {
                        frm.add_custom_button("Sync to Central Support", function () {
                            frappe.call({
                                method: "iassist.iassist.api.api.sync_to_create",
                                args: {
                                    docname: frm.doc.name,
                                    doctype: frm.doc.doctype
                                },
                                callback: function (res) {
                                    if (!res.exc) {
                                        let message = (typeof res.message === "string") 
                                            ? res.message 
                                            : JSON.stringify(res.message);

                                        frappe.msgprint(message);
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
                                        let message = (typeof res.message === "string") 
                                            ? res.message 
                                            : JSON.stringify(res.message);

                                        frappe.msgprint(message);
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
