// Copyright (c) 2024, Erpdata and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Custom Item-wise Sales Register"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			reqd: 1,
		},
		{ 
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
		{
            fieldname: "customer",
            label: __("Customer"),
            fieldtype: "MultiSelectList",
            options: "Customer",
            get_data: function(txt) {
                return frappe.db.get_link_options("Customer", txt);
            },
            reqd: 0,
        },
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
			fieldname: "mode_of_payment",
			label: __("Mode of Payment"),
			fieldtype: "Link",
			options: "Mode of Payment",
		},
		{
			fieldname: "warehouse",
			label: __("Warehouse"),
			fieldtype: "Link",
			options: "Warehouse",
		},
		{
			fieldname: "brand",
			label: __("Brand"),
			fieldtype: "Link",
			options: "Brand",
		},
		{
			fieldname: "item_code",
			label: __("Item"),
			fieldtype: "MultiSelectList",
			options: "Item",
			get_data: function(txt) {
                return frappe.db.get_link_options("Item", txt);
            },
		},
		{
			fieldname: "item_group",
			label: __("Item Group"),
			fieldtype: "MultiSelectList",
			options: "Item Group",
			get_data: function(txt) {
                return frappe.db.get_link_options("Item Group", txt);
            },
		},
		 
		{
			fieldname: "delivery_shift",
			label: __("Delivery Shift"),
			fieldtype: "Select",
			options: ["Morning","Evening"],
		},
		{
			label: __("Group By"),
			fieldname: "group_by",
			fieldtype: "Select",
			options: ["Customer Group", "Customer", "Item Group", "Item", "Territory", "Invoice"],
		},
	],
	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (data && data.bold) {
			value = value.bold();
		}
		return value;
	},
};

