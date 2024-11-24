// Copyright (c) 2024, quantdairy and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["GATE PASS SUMMARY BILL DETAILS"] = {
	"filters": [
		{
			fieldname: "from_date",
			fieldtype: "Date",
			label: "From Date",
			default:'Today',
			reqd: 1,
		},
		{
			fieldname: "to_date",
			fieldtype: "Date",
			label: "To Date",
			default:'Today',
			reqd: 1,
		},
		{
			fieldname: "Gate_pass",
			fieldtype: "Link",
			label: "Gate Pass",
			options: "Gate Pass",
			
		},
		// {
		// 	fieldname: "shift",
		// 	fieldtype: "Link",
		// 	label: "Item Group",
		// 	options: "",
			
		// },
		{
			fieldname: "route",
			fieldtype: "Link",
			label: "Route",
			options: "Route Master",
		},

	]
};
