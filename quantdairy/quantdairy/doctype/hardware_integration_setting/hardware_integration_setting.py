# Copyright (c) 2023, quantdairy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class HardwareIntegrationSetting(Document):
	pass




@frappe.whitelist()
def himeassage():
	frappe.msgprint("hiiiiiii")

@frappe.whitelist()
def hardwarelist(comport,baudrate,fat,snf,clr,water):
	frappe.msgprint("method call")
	frappe.new_doc('Hardware Integration Setting Item')
	hard_intergration = frappe.get_all('Hardware Integration Setting Item',
						filters = {'parent' :'Hardware Integration Setting',"com_port":comport},
						fields = ["name"])
	if hard_intergration:
		for d in hard_intergration:
			frappe.set_value("Hardware Integration Setting Item" , d.name ,"baud_rate",baudrate)
			frappe.set_value("Hardware Integration Setting Item" , d.name ,"fat",fat)
			frappe.set_value("Hardware Integration Setting Item" , d.name ,"snf",snf)
			frappe.set_value("Hardware Integration Setting Item" , d.name ,"clr",clr)
			frappe.set_value("Hardware Integration Setting Item" , d.name ,"water",water)
		