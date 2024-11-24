// Copyright (c) 2024, quantdairy and contributors
// For license information, please see license.txt

frappe.ui.form.on('Deduction', {
	setup(frm){
        set_filters(frm, 'paid_to', 'None', 'Account', 'is_group', '=', 0)
        set_filters(frm, 'paid_from', 'None', 'Account', 'is_group', '=', 0)
        set_filters(frm, 'cost_center', 'None', 'Cost Center', 'is_group', '=', 0)
        frm.set_query('warehouse', function(doc) {
            return {
                filters: {
                    "is_dcs":1,
                    "is_group":0,
                    "company":frappe.defaults.get_user_default("Company"),
                    "disabled":0,
                }
            };
        });
    },
	deduction_type(frm){
		if(frm.doc.deduction_type == "Farmer Loan"){
			frappe.call({
				method: "get_farmer_groups_with_deductions",
				doc:frm.doc,
				callback: function(response) {
					if (response.message) {
						const allGroup = response.message.map(group => group.name);
						frm.set_query('supplier', function(doc) {
							return {
								filters: {
									"supplier_group": ['in', allGroup],
								}
							};
						});
					}
				}
			});
		}
		if(frm.doc.deduction_type == "Transporter Loan"){
			frm.set_query('supplier', function(doc) {
				return {
					filters: {
						"is_transporter": 1,
					}
				};
			});
		}
	},
	loan_amount(frm) {
		if(frm.doc.loan_amount > 0 && frm.doc.deduction_amount_per_bill){
			frm.call({
				method: 'get_instalment',
				doc: frm.doc
			})
		}
	},
	deduction_amount_per_bill(frm){
		if(frm.doc.loan_amount > 0 && frm.doc.deduction_amount_per_bill){
			frm.call({
				method: 'get_instalment',
				doc: frm.doc
			})
		}
	},
	paid_to(frm){
		frm.set_value('credit_account',frm.doc.paid_to);
	}
});

function set_filters(frm, DocTypeFieldName, DocTypeField, Doctype, FilterField, Condition, Values){
    if(DocTypeField !== 'None'){
        frm.set_query(DocTypeFieldName, DocTypeField, function(doc, cdt, cdn) {
            return {
                filters: [
                    [Doctype, FilterField, Condition, Values],
                ]
            };
        });
    } else{
        frm.set_query(DocTypeFieldName, function(doc) {
            return {
                filters: [
                    [Doctype, FilterField, Condition, Values],
                ]
            };
        });
    }
}














// onload(frm) {
// 	if(!frm.doc.debit_account && !frm.doc.credit_account){
// 		frappe.call({
// 			method: "frappe.client.get",
// 			args: {
// 				doctype: "Dairy Settings"
// 			},
// 			callback: function(response) {
// 				if (response && response.message) {
// 					var doc = response.message;
// 					frm.set_value('debit_account',doc.loan_deduction_debit_account);
// 					frm.set_value('credit_account',doc.loan_deduction_credit_account);
// 				}
// 			}
// 		});
// 	}
// },