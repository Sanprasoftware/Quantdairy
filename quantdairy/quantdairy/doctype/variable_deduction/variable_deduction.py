# Copyright (c) 2023, quantdairy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class VariableDeduction(Document):
    pass
	# def on_submit(self):
	# 	payment=frappe.new_doc("Payment Entry")
	# 	payment.payment_type="Pay"
	# 	payment.mode_of_payment=self.mode_of_payment
	# 	payment.party_type="Supplier"
	# 	payment.party=self.farmer_code
	# 	payment.paid_amount=self.deduction_amount
	# 	payment.received_amount=self.deduction_amount
	# 	payment.paid_to=self.account
	# 	payment.paid_from=self.paid_from_account_company
	# 	if(self.reference_no):
	# 		payment.reference_no=self.reference_no
	# 	payment.insert()
	# 	self.payment_ref_link=payment.name
	# 	payment.docstatus=1
	# 	payment.custom_variable_deduction=self.name
	# 	payment.save()

	# def on_cancel(self):
	# 	frappe.throw(str(self.payment_ref_link))
	# 	frappe.throw("hi")
		# doc=frappe.get_doc("Payment Entry",self.payment_entry_doc)
		# doc.status="Cancelled"
		# doc.insert()
		# doc.save()
		# frappe.delete_doc("Payment Entry",self.payment_entry_doc,force=True)
