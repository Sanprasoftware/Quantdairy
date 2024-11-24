# Copyright (c) 2024, quantdairy and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder.functions import Coalesce, CombineDatetime
import calendar
from datetime import datetime
from frappe import _
from frappe.desk.query_report import run


def execute(filters=None):
	if not filters: filters={}
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)

	if not data:
		frappe.msgprint('🙄😵 NO RECORD FOUND 😵🙄')
	return columns, data
def add_column(fieldname,fieldtype,label,link_doc=None,uom_status=False, uom=None):
	column_li=[]
	if(link_doc!=None):
		column = {
			"fieldname": fieldname,
			"fieldtype": fieldtype,
			"label": label,
			"options":link_doc
		}
	else:
		column = {
			"fieldname": fieldname,
			"fieldtype": fieldtype,
			"label": label,
		}
	column_li.append(column)
	if(uom_status):
		temp=str(label)+" In "+str(uom)
		column = {
			"fieldname":temp,
			"fieldtype": "data",
			"label": temp,
		}
		column_li.append(column)
	return column_li

def get_columns(filters):
	column_list = []
	uom_status, uom = get_uom_status(filters)
	column_list.extend(add_column("item_code","Link","Item","Item"))
	column_list.extend(add_column("item_name", "Data", "Item Name"))
	column_list.extend(add_column("opening_stock", "Float", "Opening Stock",None, uom_status, uom))
	return column_list

def get_uom_status(filters):
	uom=filters.get("include_uom")
	uom_status=False
	if(uom):
		uom_status=True
	return uom_status,uom

def get_data(filters):
	date_filter , company_filter , item_code_filter = get_conditions(filters)
	if item_code_filter:
		item_list = [item_code_filter['item_code']]
	else:
		pass
	result_list = []
	for i in item_list:
		item_filter = {"item":i}

		item_dict['opening_stock']=get_all_available_quantity(i,filters)

	if uom_status:
			temp="Opening Stock In "+str(uom)
			item_dict[temp]=get_uom_qty(i,item_dict['opening_stock'],uom)

def get_conditions(filters):
	date_filter = {}
	company_filter = {}
	item_code_filter = {}

	company = filters.get('company')
	item_code = filters.get('item_code')
	from_date = filters.get('from_date')
	to_date = filters.get('to_date')

	# Parse from_date and to_date into datetime objects if they are not None
	if from_date:
		from_date = datetime.strptime(from_date, "%Y-%m-%d")
	if to_date:
		to_date = datetime.strptime(to_date, "%Y-%m-%d")

	if from_date and to_date:
		date_filter = {'date': ['between', [from_date, to_date]]}

	if company:
		company_filter = {'company': company}

	if item_code:
		item_code_filter = {'item_code': item_code}

	return date_filter, company_filter, item_code_filter





def get_all_available_quantity(item_code, filters): 
	from_date, to_date = get_conditions(int(filters.get('from_date')), filters.get('to_date'))
	company_name = filters.get('company')

	fiscal_year = frappe.db.sql("""
		SELECT name 
		FROM `tabFiscal Year`
		ORDER BY creation ASC
		LIMIT 1
	""", as_dict=True)

	warehouse_list = frappe.db.sql("""
		SELECT name FROM `tabWarehouse` WHERE company="{0}"
	""".format(company_name), as_dict=True)

	opn_sum = 0
	for warehouse in warehouse_list:
		opening_balance=frappe.db.sql("""
								SELECT qty_after_transaction 
								FROM `tabStock Ledger Entry` 
								WHERE posting_date < '{0}' 
									AND warehouse = '{1}' 
									AND item_code = '{2}' 
									AND fiscal_year = '{3}' 
									AND company = '{4}' 
									AND is_cancelled='{5}'
								ORDER BY creation DESC 
								LIMIT 1
								""".format(from_date,warehouse.name,item_code,fiscal_year[0].name,company_name,False),as_dict=True)
		if opening_balance:
			opn_sum += opening_balance[0].qty_after_transaction
	frappe.msgprint(str(opn_sum))
	return opn_sum
