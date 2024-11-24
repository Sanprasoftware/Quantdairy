# Copyright (c) 2023, quantdairy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class StandardDeduction(Document):
	@frappe.whitelist()
	def get_supplier_list(self):
		self.frm_items.clear()
		supp_group = frappe.get_list("Supplier Group",{'custom_apply_deduction':1})
		for sup in supp_group:
			doc=frappe.db.get_list('Supplier',filters={"dcs_id":self.warehouse__branch,"disabled":False,'supplier_group':sup['name']},
									fields=["name","supplier_name"]) 
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
		for child in self.get('frm_items'):
			child.check = 1 
   
	@frappe.whitelist()
	def get_document(self):
		self.deduction.clear()
		cow_item=""
		buffalo_item=""
		mix_item=""
		cow_litre_wise_amt=0
		cow_per_wise_amt=0
		cow_bill_wise_amt=0
		buffalo_litre_wise_amt=0
		buffalo_per_wise_amt=0
		buffalo_bill_wise_amt=0
		mix_litre_wise_amt=0
		mix_per_wise_amt=0
		mix_bill_wise_amt=0
		for type in self.get("items"):
			if(type.milk_type=="Cow"):
				cow_item=type.milk_name
			if(type.milk_type=="Buffalo"):
				buffalo_item=type.milk_name
			if(type.milk_type=="Mix"):
				mix_item=type.milk_name
			if(type.deduction_name=="Liter Wise"):
				if(type.milk_type=="Cow"):
					cow_litre_wise_amt=type.amount
				if(type.milk_type=="Buffalo"):
					buffalo_litre_wise_amt=type.amount
				if(type.milk_type=="Mix"):
					mix_litre_wise_amt=type.amount
			if(type.deduction_name=="Percentage Wise"):
				if(type.milk_type=="Cow"):
					cow_per_wise_amt=type.amount
				if(type.milk_type=="Buffalo"):
					buffalo_per_wise_amt=type.amount
				if(type.milk_type=="Mix"):
					mix_per_wise_amt=type.amount
			if(type.deduction_name=="Bill Wise"):
				if(type.milk_type=="Cow"):
					cow_bill_wise_amt=type.amount
				if(type.milk_type=="Buffalo"):
					buffalo_bill_wise_amt=type.amount
				if(type.milk_type=="Mix"):
					mix_bill_wise_amt=type.amount
		supp_group = frappe.get_list("Supplier Group",{'custom_apply_deduction':1})
		for sup in supp_group:
			doc=frappe.db.get_list('Supplier',filters={"dcs_id":self.warehouse__branch,"disabled":False,'supplier_group':sup['name']},
										fields=["name","supplier_name"]) 
	
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
										"litre_wise":cow_litre_wise_amt,
										"percentage_wise":cow_per_wise_amt,
										"bill_wise":cow_bill_wise_amt,
										"buffalo_liter_wise":buffalo_litre_wise_amt,
										"buffalo_percentage_wise":buffalo_per_wise_amt,
										"buffalo_bill_wise":buffalo_bill_wise_amt,
										"mix_liter_wise":mix_litre_wise_amt,
										"mix_percentage_wise":mix_per_wise_amt,
										"mix_bill_wise":mix_bill_wise_amt,
										"status":True,
										"cow_item":cow_item,
										"buffalo_item":buffalo_item,
										"mix_item":mix_item,
									}
								)		
		# else:
		# 	for i in self.get("frm_items"): 
		# 		if(i.check):
		# 			for d in doc:
		# 				if(i.farmer_id==d.name):
		# 					self.append(
		# 						"deduction",{
		# 							"farmer_code":d.name,
		# 							"supplier_name":d.supplier_name,
		# 							"litre_wise":cow_litre_wise_amt,
		# 							"percentage_wise":cow_per_wise_amt,
		# 							"bill_wise":cow_bill_wise_amt,
		# 							"buffalo_liter_wise":buffalo_litre_wise_amt,
		# 							"buffalo_percentage_wise":buffalo_per_wise_amt,
		# 							"buffalo_bill_wise":buffalo_bill_wise_amt,
		# 							"mix_liter_wise":mix_litre_wise_amt,
		# 							"mix_percentage_wise":mix_per_wise_amt,
		# 							"mix_bill_wise":mix_bill_wise_amt,
		# 							"status":True,
		# 							"cow_item":cow_item,
		# 							"buffalo_item":buffalo_item,
		# 							"mix_item":mix_item,
		# 						}
		# 					)
	
       
						
      
      
      
      
      
      
      
      
      
      
      
      
      
      
      
 