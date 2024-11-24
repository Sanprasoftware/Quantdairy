# Copyright (c) 2023, quantdairy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ApplyExtraRate(Document):
	@frappe.whitelist()
	def get_milk_item(self):
		for i in self.get("items"):
			milk_item=frappe.get_doc("Dairy Settings")
			if(i.milk_type=="Cow"):
				i.milk_name=milk_item.cow_pro
			elif(i.milk_type=="Buffalo"):
				i.milk_name=milk_item.buf_pro
			elif(i.milk_type=="Mix"):
				i.milk_name=milk_item.mix_pro

	@frappe.whitelist()
	def get_supplier_list(self):
		doc=frappe.db.get_list('Supplier',filters={"dcs_id":self.warehouse__branch,"disabled":False,'supplier_group':"Farmer -Milk Collection"},
								fields=["name","supplier_name"]
								) 
		farid_list=[]
		if(len(self.get("frm_items"))>0):
			for item in self.get("frm_items"):
				farid_list.append(item.farmer_id)
			for d in doc:
				if  str(d.name) not in farid_list:
					self.append(
					"frm_items",
							{
								"farmer_id": d.name,
								"farmer_name":d.supplier_name,	
							},
					)
		else:
			farmer_list=[]
			for d in doc:
				if(d.name not in farmer_list):
					farmer_list.append(d.name)
					self.append(
						"frm_items",
						{
							"farmer_id": d.name,
							"farmer_name":d.supplier_name,
						},
					)
					
	@frappe.whitelist()
	def checkall(self):
		children = self.get('frm_items')
		if not children:
			return
		all_selected = all([child.check for child in children])  
		value = 0 if all_selected else 1 
		for child in children:
			child.check = value 
   
   
	@frappe.whitelist()
	def get_document(self):
		cow_amt=0
		buffalo_amt=0
		mix_amt=0
		for type in self.get("items"):
			if(type.milk_type=="Cow"):
				cow_amt=type.amount
			if(type.milk_type=="Buffalo"):
				buffalo_amt=type.amount
			if(type.milk_type=="Mix"):
				mix_amt=type.amount
		doc=frappe.db.get_list('Supplier',filters={"dcs_id":self.warehouse__branch,"disabled":False,'supplier_group':"Farmer -Milk Collection"},
							fields=["name","supplier_name"]
							) 
  
		if(len(self.get("frm_items"))>0):
			farid_list=[]
			for item in self.get("deduction"):
				farid_list.append(item.farmer_code)
			for i in self.get("frm_items"): 
				if(i.check):
					for d in doc:
						if(i.farmer_id==d.name and i.farmer_id not in farid_list):
							self.append(
								"deduction",{
									"farmer_code":d.name,
									"supplier_name":d.supplier_name,
									"cow_item":cow_amt,
									"buffalo_item":buffalo_amt,
									"mix_item":mix_amt,
									"status":True,
								}
							)
		else:
			for i in self.get("frm_items"): 
				if(i.check):
					for d in doc:
						if(i.farmer_id==d.name):
							self.append(
								"deduction",{
									"farmer_code":d.name,
									"supplier_name":d.supplier_name,
									"cow_item":cow_amt,
									"buffalo_item":buffalo_amt,
									"mix_item":mix_amt,
									"status":True,
								}
							)