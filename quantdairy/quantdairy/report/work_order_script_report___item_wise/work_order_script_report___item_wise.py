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
        # {
        #     "fieldname": "work_order",
        #     "fieldtype": "Link",
        #     "label": "Work Order",
        #     "options": "Work Order",
        # },
        {
            "fieldname": "item",
            "fieldtype": "Link",
            "label": "Item Code",
            "options": "Item",
            
        },
        {
            "fieldname": "item_name",
            "fieldtype": "Link",
            "label": "Item Name",
            "options": "Item",
        },
                {
            "fieldname": "item_group",
            "fieldtype": "Link",
            "label": "Item Group",
			"options": "Item Group",
        },
        {
            "fieldname": "qty",
            "fieldtype": "float",
            "label": "QTY",
        },
		
		# # {
        # #     "fieldname": "customer",
        # #     "fieldtype": "Link",
        # #     "label": "Party",
        # #     "options": "Customer",
        # # },
        # {
        #     "fieldname": "route",
        #     "fieldtype": "data",
        #     "label": "Route",
        # },
        # {
        #     "fieldname": "item_code",
        #     "fieldtype": "Link",
        #     "label": "Item Code",
        #     "options": "Item",
        # },
        # {
        #     "fieldname": "uom",
        #     "fieldtype": "Data",
        #     "label": "UOM",
        # },
        # {
        #     "fieldname": "qty",
        #     "fieldtype": "float",
        #     "label": "QTY",
        # },
        # {
        #     "fieldname": "qty_per_stock_uom",
        #     "fieldtype": "float",
        #     "label": "QTY As Per Stock UOM",
        # },
        # {
        #     "fieldname": "total",
        #     "fieldtype": "float",
        #     "label": "Total",
        # },
    ]


def get_data(filters):
	
    from_date = filters.get('from_date')
    to_date =  filters.get('to_date')
    item_name = filters.get('item_name')
    item_group =  filters.get('item_group')
    item_code =  filters.get('item_code')
    conditions = []
    params = [from_date, to_date]
    # frappe.throw(str(item_code))


    sql_query = """
            SELECT 
                DATE(wo.creation) AS 'date',
                wo.production_item as 'item', 
                wo.item_name as 'item_name',
                SUM(wo.produced_qty) as 'qty', 
                i.item_group as 'item_group'
            FROM `tabWork Order` wo
            LEFT OUTER JOIN `tabItem` i on wo.production_item = i.item_code
            WHERE 
                DATE(wo.creation)  BETWEEN %s AND %s
                                            
                """
    
	
	# if production_item:
	# 	conditions.append("wo.production_item = %s")
	# 	params.append(production_item)

    if item_name:
        conditions.append("i.item_name = %s")
        params.append(item_name)

    
    if item_code:
        conditions.append("wo.production_item = %s")
        params.append(item_code)

    if conditions:
        sql_query += " AND " + " AND ".join(conditions)

    sql_query += """
                Group by wo.production_item,wo.item_name ,i.item_group
                """
    data = frappe.db.sql(sql_query, tuple(params), as_dict=True)
    return data