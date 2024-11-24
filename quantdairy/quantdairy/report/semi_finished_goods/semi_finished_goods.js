// Copyright (c) 2024, quantdairy and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Semi Finished Goods"] = {
	"filters": [
		{
			"fieldname": "company",
			"fieldtype": "Link",
			"label": "Company",
			"options": "Company",
			'reqd':1,
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},

		// {
		// 	"fieldname": "month",
		// 	"fieldtype": "Select",
		// 	"label": "Month",
		// 	"options": ["January","February","March","April","May","June","July","August","September","October","November","December"],
		// 	'reqd':1,
		// 	'default': 'December',
		// },
		// {
		// 	"fieldname": "year",
		// 	"fieldtype": "Select",
		// 	"label": "Year",
		// 	'reqd':1,
		// 	"options": [2023,2024,2025,2026,2027],

		// },
		{
			"fieldname": "item_code",
			"fieldtype": "Link",
			"label": "Item Code",
			"options": "Item",
			
		},
		 
		 
	]
};

