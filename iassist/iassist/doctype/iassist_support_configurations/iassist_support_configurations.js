// Copyright (c) 2025, New Indictrans Technologies pvt. ltd. and contributors
// For license information, please see license.txt

// frappe.ui.form.on("IAssist Support Configurations", {
// 	refresh: function (frm) {
// 		if (!frm.doc.__islocal) {
// 			frm.add_custom_button("Generate Token", function () {
// 				frappe.call({
// 					method: "iassist.iassist.doctype.iassist_support_configurations.iassist_support_configurations.generate_token_on_custom_button",
// 					callback: function (res) {
// 						if (!res.message) return;

// 						let response = res.message;

// 						frappe.msgprint({
// 							title: response.status === "success" ? __("Success") : __("Error"),
// 							indicator: response.status === "success" ? "green" : "red",
// 							message: response.message,
// 						});

// 						if (response.status === "success") {
// 							frm.reload_doc();
// 						}
// 					},
// 				});
// 			});
// 		}
// 	},
// });
