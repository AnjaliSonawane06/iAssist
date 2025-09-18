// Copyright (c) 2025, New Indictrans Technologies pvt. ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("IA Support Tickets", {
	refresh: function(frm) {
        frappe.call({
            method: "iassist.iassist.api.api.get_allowed_user",
            args: { doctype: "IAssist Support Configurations" },
            callback: function(r) {
                if (r.message && r.message == 1 && !frm.doc.custom_deleted_from_icentral_support && !frm.doc.__islocal) {
                    
                    if (!frm.doc.central_ticket_id) {
                        frm.add_custom_button("Raise Ticket", function () {
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
                    else if(!frm.doc.custom_requested_to_delete_ticket){
                        frm.add_custom_button("Update Ticket", function () {
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
                        },"Actions");


                        frm.add_custom_button("Request For Deletion", function() {
               
                        let d = new frappe.ui.Dialog({
                            title: 'Request for Deletion',
                            fields: [
                                {
                                    fieldtype: 'Small Text',
                                    fieldname: 'reason',
                                    label: 'Reason for Deletion',
                                    reqd: 1
                                }
                            ],
                            primary_action_label: 'Delete Request',
                            primary_action(values) {
                                
                            frappe.call({
                                method: "frappe.desk.form.utils.add_comment",
                                args: {
                                    reference_doctype: frm.doc.doctype,
                                    reference_name: frm.doc.name,
                                    content: values.reason,   
                                    comment_email: frappe.session.user,
                                    comment_by: frappe.session.user_fullname
                                },
                                callback: function() {
                                    
                                    frappe.call({
                                        method: "iassist.iassist.api.delete.delete_request_icentral",
                                        args: {
                                            doctype: frm.doc.doctype,
                                            docname: frm.doc.name
                                        },
                                        callback: function(res) {
                                            
                                            frappe.msgprint(res.message);
                                            frm.reload_doc();
                                            
                                        }
                                    });
                                }
                            });
                            frm.reload_doc();
                            d.hide(); 
                            }
                        });
                        frm.reload_doc();
                        d.show();
                    }, "Actions");
                

                    }
                }
            }
        });
    },
onload_post_render: function(frm) {
    frm.fields_dict && Object.keys(frm.fields_dict).forEach(fieldname => {
        frm.fields_dict[fieldname].df.onchange = () => {
            console.log("-----------------.>",frm.fields_dict)
            if (frm.doc.__unsaved) {
                frm.clear_custom_buttons();
            }
        };
    });
},
});
