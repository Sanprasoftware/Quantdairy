// Copyright (c) 2023, quantdairy and contributors
// For license information, please see license.txt

frappe.ui.form.on('Standard Deduction Type', {
	milk_type: function(frm) {
		frm.call({
			method:'get_item',
			doc: frm.doc
		});
	}
});
