# Copyright (c) 2023, quantdairy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class StandardDeductionType(Document):
	@frappe.whitelist()
	def get_item(self):
		if self.milk_type == 'Cow':
			item_code = frappe.db.get_single_value("Dairy Settings", "cow_pro")
		elif self.milk_type == 'Buffalo':
			item_code = frappe.db.get_single_value("Dairy Settings", "buf_pro")
		elif self.milk_type == 'Mix':
			item_code = frappe.db.get_single_value("Dairy Settings", "mix_pro")
		item = frappe.get_value('Item', item_code)
		self.milk_item=item