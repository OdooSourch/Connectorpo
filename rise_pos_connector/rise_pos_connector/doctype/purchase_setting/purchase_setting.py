# Copyright (c) 2024, Huda Infoteh and contributors
# For license information, please see license.txt

from faulthandler import is_enabled
import frappe
from frappe.model.document import Document
from datetime import datetime as dt
import json
import requests
import datetime
from datetime import datetime



class PurchaseSetting(Document):
	def validate(self):
		if self.enable == 0:
			self.set("api_key", '')
			self.set("auth_token", '')
			self.set("shop_code", '')
			self.set("only_special", 1)
			self.set("status", 'Inactive')

	def before_save(self):
		if self.enable == 1: 
			url = "http://dev.onegreendiary.com/erp/get_shop_purchase_orders"

			# Define the JSON payload
			payload = {
				"shop_code": self.shop_code,
				"only_special":self.only_special,
				"limit":self.limit,
				"page":self.page
			}

			# Specify the API key in the headers
			headers = {
				"api_key": self.api_key,
				"auth_token" : self.auth_token

			}

			# Make a POST request
			response = requests.post(url, json=payload, headers=headers)
			
			if response.status_code == 200:
				try:
					# Attempt to parse the JSON content of the response
					data = response.json()
					frappe.errprint(data)
					if data['status'] == 1:
						self.status = 'Active'
					else:
						frappe.msgprint("API Key and Licence No is Missing or Invalid. Try Updating Your Details.")
						self.status = 'Inactive'
						self.set("shop_code", '')
					
				except json.JSONDecodeError as e:
					frappe.msgprint(f"Error decoding JSON: {e}")
			else:
				frappe.msgprint(f"Error: {response.status_code} - {response.text}")

@frappe.whitelist()
def get_shop_purchase_orders(shop_code,api_key,auth_token,only_special,limit,page):

	url = "http://dev.onegreendiary.com/erp/get_shop_purchase_orders"

	# Define the JSON payload
	payload = {
		"shop_code": shop_code,
		"only_special": only_special,
		"limit": limit,
		"page": page
	}

	headers = {
		"api_key": api_key,
		"auth_token": auth_token
	}
	
	response = requests.post(url, json=payload, headers=headers)

	if response.status_code == 200:
		try:
			# Attempt to parse the JSON content of the response
			data = response.json()
			for shop in data['result']:
				po_number = shop.get("po_number")
				existing_po = frappe.get_value("Purchase Order", {"po_number": po_number})
				if existing_po:
					frappe.msgprint(f"Purchase Order Alrady Creted")
				else:
					# frappe.errprint(shop)
					# frappe.errprint(shop.get("name"))
					supplier_info_list = shop.get("supplier_information")	
					special_order_additional_info = shop.get("special_order_additional_info")
					# frappe.errprint(supplier_info_list)
					# for i in supplier_info_list:
					if supplier_info_list:
						po = frappe.new_doc('Purchase Order')
						po.supplier = supplier_info_list.get("name")
						po.supplier_name = shop.get("name")
						date_str = shop.get("date")
						po.supplier_id = shop.get("supplier_id")
						po.custom_shop_code = shop.get("shop_code")
						po.po_number = shop.get("po_number")
						po.is_special_order = shop.get("is_special_order")
						po.special_order_img_url = shop.get("special_order_img_url")
						po.address = shop.get("address")
						po.tax_number = shop.get("tax_number")
						po.state = shop.get("state")
						po.city = shop.get("city")
						po.phone = shop.get("phone")
						po.phone = shop.get("email")
					if special_order_additional_info:
						# po.note = special_order_additional_info.get("note") 
						# po.shape_code = special_order_additional_info.get("shape_code")
						# po.instructions = special_order_additional_info.get("instructions")
						if date_str:
							date_object = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
							formatted_date = date_object.strftime("%Y-%m-%d %H:%M:%S")
							po.transaction_date = formatted_date
						po.company = "SMB Solutions Pvt Ltd"
						po.conversion_rate = 1.00
						for item_data in shop.get("po_order_items"):
							existing_item = frappe.get_value("Item", {"item_code": item_data.get("item_code")})
							if not existing_item:
								new_item = frappe.new_doc('Item')
								new_item.item_code = item_data.get("item_code")
								new_item.item_name = item_data.get("item_code")
								new_item.item_group = "Products"
								new_item.stock_uom = "Box"
								new_item.standard_rate = item_data.get("unit_cost") 
								new_item.valuation_rate = item_data.get("unit_cost") 
								new_item.save()
							else:
								po.append("items", {
								    "item_code": item_data.get("item_code"),
								    "item_name": item_data.get("item_code"),
								    "qty": item_data.get("quantity"),
								    "schedule_date": formatted_date,
								    # "schedule_date": dt.now().strftime("%Y-%m-%d"),
								    "description": item_data.get("item_code"),
								    "uom": "Box",
								    "stock_uom": "Box",
								    "rate":item_data.get("unit_cost"),
								    "amount":item_data.get("unit_cost"),
								    # "conversion_factor": 1.00,
								    "base_rate": item_data.get("unit_cost"),
								    "base_amount": item_data.get("unit_cost"),
								    "base_amount": item_data.get("unit_cost"),
									})
						po.insert()
						frappe.db.commit()
						frappe.msgprint(f"Purchase Order created for supplier: {po.supplier} - {po.name}")
		except json.JSONDecodeError as e:
			frappe.msgprint(f"Error decoding JSON: {e}")
	else:
		frappe.msgprint(f"Error: {response.status_code} - {response.text}")