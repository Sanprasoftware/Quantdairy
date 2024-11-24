# Copyright (c) 2024, quantdairy and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    if not filters:
        filters = {}
    columns, data = [], []
    columns = get_columns(filters)
    data = get_data(filters)

    return columns, data


def get_columns(filters):
    return [
        {
            "fieldname": "date",
            "fieldtype": "Date",
            "label": "Date",
        },
        {
            "fieldname": "Code",
            "fieldtype": "Link",
            "label": "Code",
            "options": "Gate Pass",
        },
        {
            "fieldname": "Customer",
            "fieldtype": "float",
            "label": "Customer",
            
        },
		     {
            "fieldname": "Voucher",
            "fieldtype": "Data",
            "label": "Invoice",
            
        },
        {
            "fieldname": "Opening",
            "fieldtype": "Link",
            "label": "Opening",
			"options": "Crate Summary",
        },
		{
            "fieldname": "blank_data",
            "fieldtype": "Data",
            "label": "Total",
            "options": "",
        },
        {
            "fieldname": "blank_data",
            "fieldtype": "Data",
            "label": "Bank",
            "options": "",
        },
        {
            "fieldname": "blank_data",
            "fieldtype": "Data",
            "label": "Cash",            
        },
        {
           "fieldname": "blank_data",
            "fieldtype": "Data",
            "label": "Customer Sign",
        },
        {
           "fieldname": "blank_data",
            "fieldtype": "Data",
            "label": "Driver Sign",
        },
        {
            "fieldname": "blank_data",
            "fieldtype": "Data",
            "label": "Remark",
        },
        # {
        #     "fieldname": "total",
        #     "fieldtype": "float",
        #     "label": "Total",
        # },
    ]


def get_data(filters):
	
	from_date = filters.get('from_date')
	to_date =  filters.get('to_date')
	Gate_pass = filters.get('Gate Pass')
	route =  filters.get('Route Master')
	# item_name =  filters.get('item_name')
	conditions = []
	params = [from_date, to_date]

	sql_query = """
			SELECT
            DATE(g.creation) 'date',
			g.name as 'Code', 
            g.customer 'Customer', 
            c.voucher 'Voucher', 
            c.crate_opening 'Opening',
            '' as 'Total Crate',
            '' Bank,
            '' Cash,  
            '' as 'Customer Sign',
            '' Remark
			from `tabGate Pass` g
			LEFT OUTER JOIN `tabCrate Summary` c  on g.name = c.parent
            WHERE 
			    DATE(g.creation)  BETWEEN %s AND %s
			
			   
				
			
				"""

	
	# if production_item:
	# 	conditions.append("wo.production_item = %s")
	# 	params.append(production_item)

	# if item_group:
	# 	conditions.append("i.item_group = %s")
	# 	params.append(item_group)

	if Gate_pass:
		conditions.append("wo.item_name = %s")
		params.append(Gate_pass)

	if conditions:
		sql_query += " AND " + " AND ".join(conditions)

	sql_query += """
				GROUP BY g.name , customer, c.voucher, c.crate_opening
				"""
	data = frappe.db.sql(sql_query, tuple(params), as_dict=True)
	return data