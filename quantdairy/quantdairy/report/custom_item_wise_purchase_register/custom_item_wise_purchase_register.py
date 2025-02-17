# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _
from frappe.utils import flt
import erpnext
from erpnext.accounts.report.item_wise_sales_register.item_wise_sales_register import (
	add_total_row,
	get_grand_total,
	get_group_by_and_display_fields,
	get_tax_accounts,
)
from erpnext.accounts.report.utils import get_query_columns, get_values_for_columns

def add_sub_total_row(item, total_row_map, group_by_value, tax_columns):
	total_row = total_row_map.get(group_by_value)
	total_row["stock_qty"] += item["stock_qty"]
	total_row["amount"] += item["amount"]
	total_row["total_tax"] += item["total_tax"]
	total_row["total"] += item["total"]
	total_row["percent_gt"] += item["percent_gt"]

	for tax in tax_columns:
		total_row.setdefault(frappe.scrub(tax + " Amount"), 0.0)
		total_row[frappe.scrub(tax + " Amount")] += flt(item[frappe.scrub(tax + " Amount")])

def get_group_by_conditions(filters, doctype):
	if filters.get("group_by") == "Invoice":
		return "ORDER BY `tab{0} Item`.parent desc".format(doctype)
	elif filters.get("group_by") == "Item":
		return "ORDER BY `tab{0} Item`.`item_code`".format(doctype)
	elif filters.get("group_by") == "Item Group":
		return "ORDER BY `tab{0} Item`.{1}".format(doctype, frappe.scrub(filters.get("group_by")))
	elif filters.get("group_by") in ("Customer", "Customer Group", "Territory", "Supplier"):
		return "ORDER BY `tab{0}`.{1}".format(doctype, frappe.scrub(filters.get("group_by")))

def execute(filters=None):
	return _execute(filters)


def _execute(filters=None, additional_table_columns=None):
	if not filters:
		filters = {}
	columns = get_columns(additional_table_columns, filters)

	company_currency = erpnext.get_company_currency(filters.company)

	item_list = get_items(filters, get_query_columns(additional_table_columns))
	aii_account_map = get_aii_accounts()
	if item_list:
		itemised_tax, tax_columns = get_tax_accounts(
			item_list,
			columns,
			company_currency,
			doctype="Purchase Invoice",
			tax_doctype="Purchase Taxes and Charges",
		)

		scrubbed_tax_fields = {}

		for tax in tax_columns:
			scrubbed_tax_fields.update(
				{
					tax + " Rate": frappe.scrub(tax + " Rate"),
					tax + " Amount": frappe.scrub(tax + " Amount"),
				}
			)

	po_pr_map = get_purchase_receipts_against_purchase_order(item_list)

	data = []
	total_row_map = {}
	skip_total_row = 0
	prev_group_by_value = ""

	if filters.get("group_by"):
		grand_total = get_grand_total(filters, "Purchase Invoice")

	for d in item_list:
		warehouse = frappe.get_value("Purchase Invoice Item", d.name, "warehouse")
		supplier_warehouse = frappe.get_value("Supplier", d.supplier, "dcs")

		only_warehouse_set = filters.get("warehouse") and not filters.get("supplier_warehouse")
		only_supplier_warehouse_set = filters.get("supplier_warehouse") and not filters.get("warehouse")
		both_filters_set = filters.get("warehouse") and filters.get("supplier_warehouse")
		no_filters_set = not filters.get("warehouse") and not filters.get("supplier_warehouse")

		if no_filters_set:
			show_item = True  # Show all data
		elif only_warehouse_set:
			show_item = filters["warehouse"] == warehouse
		elif only_supplier_warehouse_set:
			show_item = filters["supplier_warehouse"] == supplier_warehouse
		elif both_filters_set:
			show_item = filters["warehouse"] == warehouse and filters["supplier_warehouse"] == supplier_warehouse
		else:
			show_item = False

		if not show_item:
			continue  # Skip items that don't match any condition

		purchase_receipt = d.purchase_receipt or (", ".join(po_pr_map.get(d.po_detail, [])) if d.po_detail else None)
		expense_account = (
			d.unrealized_profit_loss_account or d.expense_account or aii_account_map.get(d.company)
		)

		# Prepare the row data
		row = {
			"item_code": d.item_code,
			"item_name": d.pi_item_name or d.i_item_name,
			"item_group": d.pi_item_group or d.i_item_group,
			"gst_treatment": d.gst_treatment,
			"description": d.description,
			"invoice": d.parent,
			"posting_date": d.posting_date,
			"supplier": d.supplier,
			"supplier_name": d.supplier_name,
			**get_values_for_columns(additional_table_columns, d),
			"credit_to": d.credit_to,
			"mode_of_payment": d.mode_of_payment,
			"project": d.project,
			"company": d.company,
			"purchase_order": d.purchase_order,
			"purchase_receipt": purchase_receipt,
			"expense_account": expense_account,
			"stock_qty": d.stock_qty,
			"stock_uom": d.stock_uom,
			"rate": d.base_net_amount / d.stock_qty if d.stock_qty else d.base_net_amount,
			"amount": d.base_net_amount,
		}

		# Calculate taxes
		total_tax = 0
		for tax in tax_columns:
			item_tax = itemised_tax.get(d.name, {}).get(tax, {})
			row.update({
				scrubbed_tax_fields[tax + " Rate"]: item_tax.get("tax_rate", 0),
				scrubbed_tax_fields[tax + " Amount"]: item_tax.get("tax_amount", 0),
			})
			total_tax += flt(item_tax.get("tax_amount"))

		row.update({
			"total_tax": total_tax,
			"total": d.base_net_amount + total_tax,
			"currency": company_currency,
		})

		# Handle grouping if required
		if filters.get("group_by"):
			row.update({"percent_gt": flt(row["total"] / grand_total) * 100})
			group_by_field, subtotal_display_field = get_group_by_and_display_fields(filters)
			data, prev_group_by_value = add_total_row(
				data,
				filters,
				prev_group_by_value,
				d,
				total_row_map,
				group_by_field,
				subtotal_display_field,
				grand_total,
				tax_columns,
			)
			add_sub_total_row(row, total_row_map, d.get(group_by_field, ""), tax_columns)

		data.append(row)

	if filters.get("group_by") and item_list:
		total_row = total_row_map.get(prev_group_by_value or d.get("item_name"))
		total_row["percent_gt"] = flt(total_row["total"] / grand_total * 100)
		data.append(total_row)
		data.append({})
		add_sub_total_row(total_row, total_row_map, "total_row", tax_columns)
		data.append(total_row_map.get("total_row"))
		skip_total_row = 1

	return columns, data, None, None, None, skip_total_row


def get_columns(additional_table_columns, filters):

	columns = []

	if filters.get("group_by") != ("Item"):
		columns.extend(
			[
				{
					"label": _("Item Code"),
					"fieldname": "item_code",
					"fieldtype": "Link",
					"options": "Item",
					"width": 120,
				},
				{"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 120},
			]
		)

	if filters.get("group_by") not in ("Item", "Item Group"):
		columns.extend(
			[
				{
					"label": _("Item Group"),
					"fieldname": "item_group",
					"fieldtype": "Link",
					"options": "Item Group",
					"width": 120,
				},
				{
					"label": _("Item Tax Status"),
					"fieldname": "gst_treatment",
					"fieldtype": "Data",
					"width": 120,
				}
			]
		)

	columns.extend(
		[
			{"label": _("Description"), "fieldname": "description", "fieldtype": "Data", "width": 150},
			{
				"label": _("Invoice"),
				"fieldname": "invoice",
				"fieldtype": "Link",
				"options": "Purchase Invoice",
				"width": 120,
			},
			{"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
		]
	)

	if filters.get("group_by") != "Supplier":
		columns.extend(
			[
				{
					"label": _("Supplier"),
					"fieldname": "supplier",
					"fieldtype": "Link",
					"options": "Supplier",
					"width": 120,
				},
				{"label": _("Supplier Name"), "fieldname": "supplier_name", "fieldtype": "Data", "width": 120},
			]
		)

	if additional_table_columns:
		columns += additional_table_columns

	columns += [
		{
			"label": _("Payable Account"),
			"fieldname": "credit_to",
			"fieldtype": "Link",
			"options": "Account",
			"width": 80,
		},
		{
			"label": _("Mode Of Payment"),
			"fieldname": "mode_of_payment",
			"fieldtype": "Link",
			"options": "Mode of Payment",
			"width": 120,
		},
		{
			"label": _("Project"),
			"fieldname": "project",
			"fieldtype": "Link",
			"options": "Project",
			"width": 80,
		},
		{
			"label": _("Company"),
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Company",
			"width": 80,
		},
		{
			"label": _("Purchase Order"),
			"fieldname": "purchase_order",
			"fieldtype": "Link",
			"options": "Purchase Order",
			"width": 100,
		},
		{
			"label": _("Purchase Receipt"),
			"fieldname": "purchase_receipt",
			"fieldtype": "Link",
			"options": "Purchase Receipt",
			"width": 100,
		},
		{
			"label": _("Expense Account"),
			"fieldname": "expense_account",
			"fieldtype": "Link",
			"options": "Account",
			"width": 100,
		},
		{"label": _("Stock Qty"), "fieldname": "stock_qty", "fieldtype": "Float", "width": 100},
		{
			"label": _("Stock UOM"),
			"fieldname": "stock_uom",
			"fieldtype": "Link",
			"options": "UOM",
			"width": 100,
		},
		{
			"label": _("Rate"),
			"fieldname": "rate",
			"fieldtype": "Float",
			"options": "currency",
			"width": 100,
		},
		{
			"label": _("Amount"),
			"fieldname": "amount",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 100,
		},
	]

	if filters.get("group_by"):
		columns.append(
			{"label": _("% Of Grand Total"), "fieldname": "percent_gt", "fieldtype": "Float", "width": 80}
		)

	return columns


def get_conditions(filters):
	conditions = ""
	
	for opts in (
		("company", " and `tabPurchase Invoice`.company=%(company)s"),
		("supplier", " and `tabPurchase Invoice`.supplier in %(supplier)s"),
		("supplier_group", " and `tabPurchase Invoice`.supplier_group in %(supplier_group)s"),
		("item_code", " and `tabPurchase Invoice Item`.item_code in %(item_code)s"),
		("item_group", " and `tabPurchase Invoice Item`.item_group in %(item_group)s"),
		("from_date", " and `tabPurchase Invoice`.posting_date>=%(from_date)s"),
		("to_date", " and `tabPurchase Invoice`.posting_date<=%(to_date)s"),
		("mode_of_payment", " and ifnull(mode_of_payment, '') = %(mode_of_payment)s"),
	):
		if filters.get(opts[0]):
			conditions += opts[1]

	if not filters.get("group_by"):
		conditions += (
			"ORDER BY `tabPurchase Invoice`.posting_date desc, `tabPurchase Invoice Item`.item_code desc"
		)
	else:
		conditions += get_group_by_conditions(filters, "Purchase Invoice")

	return conditions


def get_items(filters, additional_query_columns):
	conditions = get_conditions(filters)
	# frappe.throw(str(conditions))
	if additional_query_columns:
		additional_query_columns = "," + ",".join(additional_query_columns)
	return frappe.db.sql(
		"""
		select
			`tabPurchase Invoice Item`.`name`, 
			`tabPurchase Invoice Item`.`gst_treatment`, 
			`tabPurchase Invoice Item`.`parent`,
			`tabPurchase Invoice`.posting_date, `tabPurchase Invoice`.credit_to, `tabPurchase Invoice`.company,
			`tabPurchase Invoice`.supplier, `tabPurchase Invoice`.remarks, `tabPurchase Invoice`.base_net_total,
			`tabPurchase Invoice`.unrealized_profit_loss_account,
			`tabPurchase Invoice Item`.`item_code`, `tabPurchase Invoice Item`.description,
			`tabPurchase Invoice Item`.`item_name` as pi_item_name, `tabPurchase Invoice Item`.`item_group`
			,`tabPurchase Invoice Item`.`item_group` as pi_item_group,
			`tabItem`.`item_name` as i_item_name, `tabItem`.`item_group` as i_item_group,
			`tabPurchase Invoice Item`.`project`, `tabPurchase Invoice Item`.`purchase_order`,
			`tabPurchase Invoice Item`.`purchase_receipt`, `tabPurchase Invoice Item`.`po_detail`,
			`tabPurchase Invoice Item`.`expense_account`, `tabPurchase Invoice Item`.`stock_qty`,
			`tabPurchase Invoice Item`.`stock_uom`, `tabPurchase Invoice Item`.`base_net_amount`,
			`tabPurchase Invoice`.`supplier_name`, `tabPurchase Invoice`.`mode_of_payment` {0}
		from `tabPurchase Invoice`, `tabPurchase Invoice Item`, `tabItem`
		where `tabPurchase Invoice`.name = `tabPurchase Invoice Item`.`parent` and
			`tabItem`.name = `tabPurchase Invoice Item`.`item_code` and
			`tabPurchase Invoice`.docstatus = 1 {1}
	""".format(
			additional_query_columns, conditions
		),
		filters,
		as_dict=1,
	)


def get_aii_accounts():
	return dict(frappe.db.sql("select name, stock_received_but_not_billed from tabCompany"))


def get_purchase_receipts_against_purchase_order(item_list):
	po_pr_map = frappe._dict()
	po_item_rows = list(set(d.po_detail for d in item_list))

	if po_item_rows:
		purchase_receipts = frappe.db.sql(
			"""
			select parent, purchase_order_item
			from `tabPurchase Receipt Item` 
			where docstatus=1 and purchase_order_item in (%s)
			group by purchase_order_item, parent
		"""
			% (", ".join(["%s"] * len(po_item_rows))),
			tuple(po_item_rows),
			as_dict=1,
		)

		for pr in purchase_receipts:
			po_pr_map.setdefault(pr.po_detail, []).append(pr.parent)

	return po_pr_map
