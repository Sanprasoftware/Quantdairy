# Copyright (c) 2024, quantdairy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TankerInwardOutward(Document):
	def before_save(self):
		total_quantity = 0
		total_basic = 0
		total_basic_amount = 0
		for i in self.tanker_division:
			total_quantity += i.quantity
			total_basic += i.basic
			total_basic_amount += i.basic_amount
		self.total_quantity = total_quantity
		self.total_basic = total_basic
		self.total_basic_amount = total_basic_amount

	@frappe.whitelist()
	def add_division_row(self):
		self.tanker_division.clear()
		if self.no_of_division:
			for i in range(int(self.no_of_division)):
				self.append('tanker_division',{'division':f'Division {i+1}','cmbm':'Cow'})
