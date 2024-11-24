// Copyright (c) 2023, quantdairy and contributors
// For license information, please see license.txt

frappe.ui.form.on('Standard Deduction', {
	refresh: function(frm) {
        $('.layout-side-section').hide();
        $('.layout-main-section-wrapper').css('margin-left', '0');
    },
	get_farmer_list: function (frm) {
		frm.call({
			method: 'get_supplier_list',//function name defined in python
			doc: frm.doc, //current document
		});
	},
	check_all: function (frm) {
		frm.call({
			method: 'checkall',//function name defined in python
			doc: frm.doc, //current document
		});
	},
	show: function(frm) {
		frm.call({
			method: 'get_document',//function name defined in python
			doc: frm.doc, //current document
		});	
	}
});
frappe.ui.form.on('Standard Deduction Item', {
    deduction_type: function(frm,cdt,cdn) {
        var deduction_type_list = [];
        frm.doc.items.forEach(function(row) {
            deduction_type_list.push(row.deduction_type);
        });
		frm.set_query("deduction_type","items",function(doc, cdt, cdn) {
			let d = locals[cdt][cdn];
            return {
                filters: [
                    ['Standard Deduction Type', 'name','not in', deduction_type_list],
                ]
            };
        });
    }
});





