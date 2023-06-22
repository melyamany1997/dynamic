# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt

from pickle import TRUE
import re
import frappe
from frappe.model.document import Document
from frappe import _ 
class Reservation(Document):

	def validate(self):
		target ='warehouse' if not self.order_source else 'pur'
		if target == 'warehouse' :
			data = self.validate_warehouse()
		if target == 'pur':
			data = self.validate_purchase_order()
		self.total_warehouse_reseved()
		self.total_purchase_order_reseved()
		
	def validate_warehouse(self):
		stock_sql = self.stock_sql()
		if stock_sql and len(stock_sql) > 0 :
			if stock_sql[0].get("qty") == 0 or float( stock_sql[0].get("qty")  or 0 ) < self.reservation_amount  :
				frappe.throw(_(f""" stock value in warehouse {self.warehouse_source} = {stock_sql[0].get("qty")} 
				  and you requires  {self.reservation_amount} for ITem {self.item_code}  """))
			self.warehouse = [] #?add row
			row = self.append('warehouse', {})
			row.item = self.item_code
			row.bin = stock_sql[0].get("bin") 
			row.warehouse = self.warehouse_source
			row.current_available_qty = stock_sql[0].get("qty") 
			row.reserved_qty = self.reservation_amount
			row.available_qty_atfer___reservation = stock_sql[0].get("qty") - self.reservation_amount
		if  not stock_sql or len(stock_sql) == 0 :
			# return {'falge':False,'msg':""" no stock value in warehouse {self.warehouse_source} for item {self.item_code}  """}
			frappe.throw(_(f"""no stock value in warehouse {self.warehouse_source} for item {self.item_code}  """))

	def stock_sql(self):
		"""get bin which its choosen and check its qty before this transaction and reserv name != self.name"""
		data = frappe.db.sql(f""" 
				SELECT `tabBin`.name as bin , 'Bin' as `doctype`,
				CASE 
						WHEN `tabReservation Warehouse`.reserved_qty > 0 
						then `tabBin`.actual_qty - SUM(`tabReservation Warehouse`.reserved_qty)
						ELSE `tabBin`.actual_qty 
						END  as qty
				FROM 
				`tabBin`
				LEFT JOIN 
				`tabReservation Warehouse`
				ON `tabBin`.name = `tabReservation Warehouse`.bin 
				LEFT JOIN 
				`tabReservation` 
				ON `tabReservation Warehouse`.parent = `tabReservation`.name 
				AND `tabBin`.name = `tabReservation Warehouse`.bin
				WHERE `tabBin`.warehouse = '{self.warehouse_source}'
				AND `tabBin`.item_code = '{self.item_code}'
				AND `tabReservation`.name <> "{self.name}"
				AND `tabReservation`.status  <> "Invalid"
				""" ,as_dict=1)
		
		if data and len(data) > 0 :
			if data[0].get("qty") == 0 or float( data[0].get("qty")  or 0 ) < self.reservation_amount  :
				frappe.throw(_(f""" stock value in warehouse {self.warehouse_source} = {data[0].get("qty")} 
				  and you requires  {self.reservation_amount} for ITem {self.item_code}  """))
		if  not data or len(data) == 0 :
			frappe.throw(_(f"""no stock value in warehouse {self.warehouse_source} for item {self.item_code}  """))

		return data

	def validate_purchase_order(self):
		order =  frappe.db.sql(f"""                   
			SELECT `tabPurchase Order Item`.name as `name` ,`tabPurchase Order Item`.parent,`tabPurchase Order Item`.parenttype as doctype,
			CASE
				WHEN `tabReservation Purchase Order`.reserved_qty > 0 
				then (`tabPurchase Order Item`.qty - `tabPurchase Order Item`.received_qty) - SUM(`tabReservation Purchase Order`.reserved_qty)
				else `tabPurchase Order Item`.qty - `tabPurchase Order Item`.received_qty
			end as qty
			from
			`tabPurchase Order Item`
			LEFT JOIN
			`tabReservation Purchase Order`
			ON `tabReservation Purchase Order`.purchase_order_line=`tabPurchase Order Item`.name 
			LEFT JOIN
			`tabReservation`
			ON `tabReservation Purchase Order`.parent = `tabReservation`.name 
			AND `tabReservation`.name <> '{self.name}' AND  `tabReservation`.status <> "Invalid"
			where `tabPurchase Order Item`.item_code = '{self.item_code}'  
			AND `tabPurchase Order Item`.parent = '{self.order_source}' 
			""",as_dict=1)
		if order and len(order) > 0 :
			if order[0].get("name") and float(order[0].get("qty")) > 0 :
				if order[0].get('qty') < self.reservation_amount :
					frappe.throw(_(f"Pruchase Order  {self.order_source} = {order[0].get('qty')} and you requires  {self.reservation_amount} "))
				if self.reservation_amount <= order[0].get('qty') :
					self.reservation_purchase_order = [] #?add row
					row = self.append('reservation_purchase_order', {})
					row.item = self.item_code
					row.purchase_order_line = order[0].get("name")
					row.purchase_order = self.order_source
					row.qty = self.reservation_amount
					row.reserved_qty = self.reservation_amount
					row.current_available_qty = float(order[0].get("qty"))
					row.available_qty_atfer___reservation = float(order[0].get("qty")) - self.reservation_amount

			if order[0].get("parent") and float(order[0].get("qty")) ==  0 :
				frappe.throw(_(f"  Purchase Order {self.order_source} don't have {self.item_code} Qty and you requires  {self.reservation_amount}" ))
			if not order[0].get("parent") :
				frappe.throw(_(f"  Purchase Order {self.order_source} don't have item {self.item_code}" ))	
		if not order or  len(order) == 0 :
			frappe.throw(_(f"Invalid Purchase Order {self.order_source} don't have item {self.item_code}"))
	

	def total_warehouse_reseved(self):
		total_warehouse=0
		for row in self.warehouse:
			total_warehouse += float(row.reserved_qty)
		self.db_set('total_warehouse_reseved_qty',total_warehouse)
	
	def total_purchase_order_reseved(self):
		total_put_order=0
		for row in self.reservation_purchase_order:
			total_put_order += float(row.reserved_qty)
		self.db_set('total_purchase_order_reserved_qty',total_put_order)

	
