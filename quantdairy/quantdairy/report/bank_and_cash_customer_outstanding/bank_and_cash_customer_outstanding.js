// Copyright (c) 2024, quantdairy and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Bank and Cash Customer Outstanding"] = {
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
			label: __("Customer"),
			fieldtype: "MultiSelectList",
			options: "Customer",
			get_data: function(txt) {
				return frappe.db.get_link_options("Customer", txt);
			},
			reqd: 0,
		},
		// {
		// 	fieldname: "party",
		// 	label: __("Customer"),
		// 	fieldtype: "Link",
		// 	options: "Customer",

		// 	on_change: () => {
		// 		var party = frappe.query_report.get_filter_value("party");
		// 		if (party) {
		// 			frappe.db.get_value("Customer", party, ["tax_id", "customer_name"], function (value) {
		// 				frappe.query_report.set_filter_value("tax_id", value["tax_id"]);
		// 				frappe.query_report.set_filter_value("customer_name", value["customer_name"]);
		// 			});
		// 		} else {
		// 			frappe.query_report.set_filter_value("tax_id", "");
		// 			frappe.query_report.set_filter_value("customer_name", "");
		// 		}
		// 	},
		// },
		{
			fieldname: "customer_group",
			label: __("Customer Group"),
			fieldtype: "MultiSelectList",
			options: "Customer Group",
			get_data: function(txt) {
				return frappe.db.get_link_options("Customer Group", txt);
			},
			reqd: 0,
		},
		{
			fieldname: "territory",
			label: __("Territory"),
			fieldtype: "Link",
			options: "Territory",
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
		
		// {
		// 	fieldname: "delivery_shift",
		// 	label: __("Delivery Shift"),
		// 	fieldtype: "Select",
		// 	options: [" ","Morning","Evening"],
		// },
		
	]
};
