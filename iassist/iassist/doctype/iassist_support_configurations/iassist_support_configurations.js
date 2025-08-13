// Copyright (c) 2025, New Indictrans Technologies pvt. ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("IAssist Support Configurations", {
	refresh: function (frm) {
		show_multi_user(frm)
	},
	is_multiple_users: function(frm){
		show_multi_user(frm)
	}
});


function show_multi_user(frm){
	if (frm.doc.is_multiple_users== 0) {
        	frm.set_df_property('ics_multi_user_details', 'hidden', 1);
    		frm.set_df_property('username', 'hidden', 0);
			frm.set_df_property('password', 'hidden', 0);
			frm.set_df_property('api_key', 'hidden', 0);
			frm.set_df_property('api_secret', 'hidden', 0);
	}
	if (frm.doc.is_multiple_users== 1) {
        	frm.set_df_property('ics_multi_user_details', 'hidden', 0);
			frm.set_df_property('username', 'hidden', 1);
			frm.set_df_property('password', 'hidden', 1);
			frm.set_df_property('api_key', 'hidden', 1);
			frm.set_df_property('api_secret', 'hidden', 1);
		
	
	}
}
