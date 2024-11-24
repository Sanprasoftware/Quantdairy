// Copyright (c) 2024, quantdairy and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Milk Entry Vs Tanker Process"] = {
	"filters": [
		{"label": "From Date", "fieldname": "from_date", "fieldtype": "Date", "reqd": 1},
		{"label": "To Date", "fieldname": "to_date", "fieldtype": "Date", "reqd": 1},
		{"label": "From Shift", "fieldname": "from_shift", "fieldtype": "Select", "options":"Morning\nEvening", "reqd": 1},
		{"label": "To Shift", "fieldname": "to_shift", "fieldtype": "Select", "options":"Morning\nEvening", "reqd": 1},
		{"label": "DCS", "fieldname": "dcs", "fieldtype": "MultiSelectList", "options":"Warehouse",get_data: function(txt) {
			return frappe.db.get_link_options("Warehouse", txt);
		}},
	]
};

// frappe.query_reports["Milk Entry Vs Tanker Process"] = {
// 	"filters": [
// 		{"label": "From Date", "fieldname": "from_date", "fieldtype": "Date", "reqd": 1},
// 		{"label": "To Date", "fieldname": "to_date", "fieldtype": "Date", "reqd": 1},
// 		{"label": "Shift", "fieldname": "shift", "fieldtype": "Select", "options":"\nMorning\nEvening"},
// 		{"label": "DCS", "fieldname": "dcs", "fieldtype": "MultiSelectList", "options":"Warehouse",get_data: function(txt) {
// 			return frappe.db.get_link_options("Warehouse", txt);
// 		}},
// 	]
// };