// Copyright (c) 2023, quantdairy and contributors
// For license information, please see license.txt

// frappe.ui.form.on('Variable Deduction', {
	
// });


frappe.ui.form.on('Variable Deduction', {
	refresh: function(frm){
		if(frm.doc.is_deducted == 1){
			frm.set_df_property("farmer_code", "read_only", 1);
			frm.set_df_property("deduction_name", "read_only", 1);
			frm.set_df_property("deduction_amount", "read_only", 1);
			frm.set_df_property("warehouse_branch", "read_only", 1);
		}
	},
	setup: function(frm) {
		frm.set_query("farmer_code", function(doc) {
			return {
				filters: [
				    ['Supplier', 'dcs_id', '=', frm.doc.warehouse_branch],
				]
			};
		});
	},
	paid_from_account_name: function(frm) {
		frm.set_query("paid_from_account_name", function(doc) {
			return {
				filters: [
				    ['Bank Account', 'is_company_account', '=', true],
				]
			};
		});
	}

})
