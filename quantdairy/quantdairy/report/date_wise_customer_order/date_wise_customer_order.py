# Copyright (c) 2024, quantdairy and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime, timedelta

def execute(filters=None):
    if not filters:
        filters = {}
    columns, data = [], []
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
     
    final_col =[ {
                    "fieldname": "customer",
                    "fieldtype": "Link",
                    "label": "Party",
                    "options": "Customer",
                },
                {
                    "fieldname": "customer_name",
                    "fieldtype": "Data",
                    "label": "Customer Name",
                },]
    
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    start_date = datetime.strptime(from_date, "%Y-%m-%d")
    end_date = datetime.strptime(to_date, "%Y-%m-%d")
    current_date = start_date
    while current_date <= end_date:
        date = {}
        date ={
            "fieldname": str(current_date.strftime("%d-%m-%Y")),
            "fieldtype": "Data",
            "label": str(current_date.strftime("%d-%m-%Y")),
        }
        final_col.append(date)
        current_date += timedelta(days=1)
    return final_col

def get_data(filters):
    final_data = []
    from_date = filters.get('from_date')
    to_date = filters.get('to_date')
    customer = filters.get('customer')
    customer_name = filters.get('customer_name')
    conditions = []
    params = [from_date, to_date]
    sql_query = """
        SELECT DISTINCT
            customer,
            customer_name,
            transaction_date
        FROM 
            `tabSales Order`
        WHERE 
            transaction_date BETWEEN %s AND %s

    """

    if customer:
        conditions.append("customer = %s")
        params.append(customer)

    if customer_name:
        conditions.append("customer_name = %s")
        params.append(customer_name)

    if conditions:
        sql_query += " AND " + " AND ".join(conditions)

     

    data = frappe.db.sql(sql_query, tuple(params), as_dict=True)
    # frappe.throw(str(data))


    output = {}

    if data :
        for item in data:
            formatted_date = item['transaction_date'].strftime("%d-%m-%Y")
            
            if item['customer'] not in output:
                output[item['customer']] = {'customer': item['customer'], 'customer_name': item['customer_name']}
            
            customer_record = output[item['customer']]

            if formatted_date not in customer_record:
                customer_record[formatted_date] = '✔'


    start_date = datetime.strptime(from_date, "%Y-%m-%d")
    end_date = datetime.strptime(to_date, "%Y-%m-%d")
    current_date = start_date
    while current_date <= end_date:
        formatted_date = current_date.strftime("%d-%m-%Y")
        for customer_record in output.values():
            if formatted_date not in customer_record:
                customer_record[formatted_date] = '❌'
        current_date += timedelta(days=1)
 
    output = list(output.values())
    return output
        
 
    output = list(output.values())
    return output
 