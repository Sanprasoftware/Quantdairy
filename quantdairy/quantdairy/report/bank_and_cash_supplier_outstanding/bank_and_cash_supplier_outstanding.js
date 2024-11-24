// Copyright (c) 2024, quantdairy and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Bank and Cash Supplier Outstanding"] = {
	"filters": [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			reqd: 1,
			width: "60px",
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
			width: "60px",
		},
		{
			fieldname: "party",
			label: __("Supplier"),
			fieldtype: "MultiSelectList",
			options: "Supplier",
			get_data: function(txt) {
				return frappe.db.get_link_options("Supplier", txt);
			},
			reqd: 0,
		},
		{
			fieldname: "supplier_group",
			label: __("Supplier Group"),
			fieldtype: "MultiSelectList",
			options: "Supplier Group",
			get_data: function(txt) {
				return frappe.db.get_link_options("Supplier Group", txt);
			},
			reqd: 0,
		},
		{
			fieldname: "mode_of_payment",
			label: __("Mode of Payment"),
			fieldtype: "MultiSelectList",
			options: "Mode of Payment",
			get_data: function(txt) {
				return frappe.db.get_link_options("Mode of Payment", txt);
			},
			reqd: 0,
		},
	]
};
