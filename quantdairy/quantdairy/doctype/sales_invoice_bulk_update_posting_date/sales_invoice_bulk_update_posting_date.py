# Copyright (c) 2024, quantdairy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SalesInvoiceBulkUpdatePostingDate(Document):
    
	def before_save(self):
		if self.posting_date and self.payment_due_date:
			if self.payment_due_date <= self.posting_date :
				frappe.throw("Due Date cannot be before Posting / Supplier Invoice Date")

	@frappe.whitelist()
	def set_salein_date(self):
		if self.from_date and self.to_date:
			sale = frappe.get_list("Sales Invoice", 
						filters={"posting_date": ["between", [self.from_date, self.to_date]],"docstatus":0},
						fields=["name","posting_date","posting_time","due_date","customer","customer_name"])
			# frappe.throw(str(doc))
			if (sale):
				for d in sale:
					self.append('date_update',{
							"invoice_no":d.name,
							"posting_date":d.posting_date,
							"posting_time" :d.posting_time,
							"payment_due_date":d.due_date,
							"customer":d.customer,
							"customer_name":d.customer_name

					})
				

	@frappe.whitelist()
	def update_date(self):
		for i in self.get("date_update"):
			if i.check and self.posting_date:
				frappe.db.set_value("Sales Invoice", i.invoice_no, "posting_date", self.posting_date)
				frappe.db.set_value("Sales Invoice", i.invoice_no, "posting_time", self.posting_time)
				frappe.db.set_value("Sales Invoice", i.invoice_no, "due_date", self.payment_due_date)
		
		payment = frappe.get_all("Payment Schedule",filters = {'parent':i.invoice_no})
		if payment:
			for p in payment:
				frappe.db.set_value("Payment Schedule", p.name, "due_date", self.payment_due_date)

	@frappe.whitelist()
	def selectall(self):
		children = self.get('date_update')
		if not children:
			return
		all_selected = all([child.check for child in children])  
		value = 0 if all_selected else 1 
		for child in children:
			child.check = value
			