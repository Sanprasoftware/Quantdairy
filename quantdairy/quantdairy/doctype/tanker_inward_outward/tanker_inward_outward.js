// Copyright (c) 2024, quantdairy and contributors
// For license information, please see license.txt
frappe.ui.form.on('Tanker Inward Outward', {
    onload: function(frm) {
        frm.trigger("hide_add_row");
    },
    refresh: function(frm) {
        frm.trigger("hide_add_row");
    },
    hide_add_row: function (frm) {
        frm.fields_dict['tanker_division'].grid.wrapper.find('.grid-add-row').hide();
    },
    no_of_division: function(frm) {
        frm.call({
            method: 'add_division_row',
            doc: frm.doc,
            callback: function() {
                frm.trigger("hide_add_row");
            }
        });
    }
});


frappe.ui.form.on("Tanker Inward Divison", {
    quantity: function(frm, cdt, cdn) {
        const row = frappe.get_doc(cdt, cdn);
        row.quantity_kg = parseFloat(row.quantity) * 1.03;
        frm.refresh_field("tanker_division");
        frm.trigger("hide_add_row");
    },
    quantity_kg: function(frm, cdt, cdn) {
        const row = frappe.get_doc(cdt, cdn);
        row.quantity = parseFloat(row.quantity_kg) * .9707;
        frm.refresh_field("tanker_division");
        frm.trigger("hide_add_row");
    },
    basic: function(frm, cdt, cdn) {
        const row = frappe.get_doc(cdt, cdn);
        row.basic_amount = parseFloat(row.basic) * parseFloat(row.quantity);
        frm.refresh_field("tanker_division");
        frm.trigger("hide_add_row");
    },
});


