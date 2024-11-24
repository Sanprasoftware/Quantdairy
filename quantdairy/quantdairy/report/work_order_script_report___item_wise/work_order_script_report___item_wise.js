// Copyright (c) 2024, quantdairy and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Work Order Script Report - Item wise"] = {
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
			fieldname: "Company",
			fieldtype: "Link",
			label: "Item Code",
			options: "Production",
			
		},
		{
			fieldname: "item_group",
			fieldtype: "Link",
			label: "Item Group",
			options: "Item Group",
			
		},
		// {
		// 	fieldname: "item_name",
		// 	fieldtype: "Link",
		// 	label: "Item Name",
		// 	options: "Item",
			
		// },
		// {
		// 	fieldname: "route",
		// 	fieldtype: "Link",
		// 	label: "Route",
		// 	options: "Route Master",
		// },

	]
};
