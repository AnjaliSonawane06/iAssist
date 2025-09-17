// Copyright (c) 2025, New Indictrans Technologies pvt. ltd. and contributors
// For license information, please see license.txt


frappe.ui.form.on("IAssist Support Configurations", {
    refresh: function (frm) {
        if(!frm.doc.__islocal){
        frm.add_custom_button("Generate Token", function () {
            frappe.call({
                method: "iassist.iassist.doctype.iassist_support_configurations.iassist_support_configurations.generate_token_on_custom_button",
                callback: function (res) {
                    if (!res.exc) {
						let message = (typeof res.message === "string") 
							? res.message 
							: JSON.stringify(res.message);
						frappe.msgprint("Token generated successfully");
						frm.reload_doc();
                    } else {
                        frappe.msgprint({
                            title: __("Error"),
                            indicator: "red",
                            message: __("Could not generate token. Please check logs.")
                        });
                    }
                }
            });
        });
    }
    }
});


