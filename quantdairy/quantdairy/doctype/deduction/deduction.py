# Copyright (c) 2024, quantdairy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Deduction(Document):
	def before_submit(self):
		if self.deduction_type == "Farmer Loan" or self.deduction_type == "Transporter Loan":
			self.make_payment_entry()
	def before_save(self):
		self.get_instalment()

	def make_payment_entry(self):
		payment=frappe.new_doc("Payment Entry")
		payment.payment_type="Pay"
		payment.mode_of_payment=self.mode_of_payment
		payment.party_type="Supplier"
		payment.party=self.supplier
		payment.paid_amount=self.loan_amount
		payment.received_amount=self.loan_amount
		payment.paid_to=self.paid_to
		payment.paid_from=self.paid_from
		payment.cost_center=self.cost_center
		payment.custom_deduction=self.name
		payment.insert()
		# payment.save()
		payment.submit()

	@frappe.whitelist()
	def get_instalment(self):
		self.deduction_instalment_list.clear()
		amount = self.loan_amount
		ded_amount = self.deduction_amount_per_bill
		while amount > 0:
			instalment_amount = min(ded_amount, amount)
			self.append('deduction_instalment_list', {
				'instalment_amount': instalment_amount,
			})
			amount -= instalment_amount

	@frappe.whitelist()
	def get_farmer_groups_with_deductions(self):
		return frappe.db.get_all("Supplier Group", filters={'custom_apply_deduction': 1})
