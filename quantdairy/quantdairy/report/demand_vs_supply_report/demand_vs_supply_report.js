// Copyright (c) 2024, quantdairy and contributors
// For license information, please see license.txt
/* eslint-disable */

// frappe.query_reports["Demand vs Supply Report"] = {
// 	"filters": [

// 	]
// };

frappe.query_reports["Demand vs Supply Report"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Company",
			"reqd": 1,
			"default": frappe.defaults.get_default("company")
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

		{
			"fieldname":"delivery_shift",
			"label": __("Shift"),
			"fieldtype": "Select",
			"options": ["","Morning", "Evening"] ,
			"width": "80",
		},
		
		{
			"fieldname":"item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"width": "80",
		},
		{
			"fieldname":"item_name",
			"label": __("Item Name"),
			"fieldtype": "Link",
			"options": "Item",
			"width": "80",
		},
		{
			"fieldname": "route",
			"label": __("Route Wise"),
			"fieldtype": "Link",
			"options": "Route Master",
			"width": "80",
			// "get_query": function() {
			// 	var route = frappe.query_report_filters_by_name.route.get_value();
			// 	return {
			// 		doctype: "Sales Order",
			// 		filters: {route: route}
			// 	}
			// }
		},
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": "80",
		},
		{
			"fieldname": "sales_order",
			"label": __("Sales Order"),
			"fieldtype": "MultiSelectList",
			"width": "80",
			"options": "Sales Order",
			"get_data": function(txt) {
				return frappe.db.get_link_options("Sales Order", txt);
			},
			"get_query": () =>{
				return {
					filters: { "docstatus": 1 }
				}
			}
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "MultiSelectList",
			"width": "80",
			get_data: function(txt) {
				let status = ["To Bill", "To Deliver", "To Deliver and Bill", "Completed", "Closed"]
				let options = []
				for (let option of status){
					options.push({
						"value": option,
						"label": __(option),
						"description": ""
					})
				}
				return options
			}
		},
		{
			"fieldname": "group_by_so",
			"label": __("Group by Sales Order"),
			"fieldtype": "Check",
			"default": 0
		}
	],

	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		let format_fields = ["delivered_qty", "billed_amount"];

		if (in_list(format_fields, column.fieldname) && data && data[column.fieldname] > 0) {
			value = "<span style='color:green;'>" + value + "</span>";
		}

		if (column.fieldname == "delay" && data && data[column.fieldname] > 0) {
			value = "<span style='color:red;'>" + value + "</span>";
		}
		return value;
	}
};