// Copyright (c) 2023, quantdairy and contributors
// For license information, please see license.txt

frappe.ui.form.on('Apply Extra Rate', {
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
frappe.ui.form.on('Child extra rate Item', {
	milk_type: function (frm) {
		frm.call({
			method: 'get_milk_item',//function name defined in python
			doc: frm.doc, //current document
		});
	}
});