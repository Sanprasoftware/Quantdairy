// Copyright (c) 2024, quantdairy and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Invoice Bulk Update Posting Date', {
	sales_invoices: function(frm) {
		frm.call({
			method: 'set_salein_date',//function name defined in python
			doc: frm.doc, //current document
		});
	}
});

frappe.ui.form.on('Sales Invoice Bulk Update Posting Date', {
	after_save: function(frm) {
		frm.call({
			method: 'update_date',//function name defined in python
			doc: frm.doc, //current document
		});
	}
});
frappe.ui.form.on('Sales Invoice Bulk Update Posting Date', {
	select_all: function(frm) {
		frm.call({
			method: 'selectall',//function name defined in python
			doc: frm.doc, //current document
		});
	}
});

