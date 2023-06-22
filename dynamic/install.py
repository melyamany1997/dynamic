import frappe
import os
import json


def create_currency_exchange_rate_script():
	""" recalculate paid amount if exchange rate changed"""
	try:
		if not frappe.db.exists("Client Script","Payment Entry-Form") :
			doc = frappe.new_doc("Client Script")
			doc.dt      = "Payment Entry"
			doc.view    = "Form"
			doc.enabled = 0
			doc.script = """
				frappe.ui.form.on('Payment Entry', {
					target_exchange_rate:(frm)=>{
						let paid_amount = frm.doc.target_exchange_rate * frm.doc.received_amount
						frm.set_value("paid_amount",paid_amount)
						frm.refresh_field("paid_amount")
						console.log("hellow",paid_amount)
					}
				})
				"""
			doc.save()
	except:
		pass

def create_invoice_custom_field():
	"""create return field in sales invoice to display it general ledger report"""
	try:
		if not frappe.db.exists("Custom Field","Sales Invoice-is_return_inv"):
			doc = frappe.new_doc("Custom Field")
			doc.dt = "Sales Invoice"
			doc.label = "Return"
			doc.fieldname = "is_return_inv"
			doc.fieldtype = "Data"
			doc.read_only = 1
			doc.hidden    = 1
			doc.save()
	except:
		pass
def create_sales_invoice_script():
	"""set return field if is return checked"""
	try:
		if not frappe.db.exists("Client Script","Sales Invoice-Form") :
			doc = frappe.new_doc("Client Script")
			doc.dt      = "Sales Invoice"
			doc.view    = "Form"
			doc.enabled = 1
			doc.script = """
				frappe.ui.form.on('Sales Invoice', {
					is_reurn:(frm)=>{
						if(frm.doc.is_return ==1){
							frm.set_value("is_return_inv","مرتجع-Return")
						}
					},
					before_save:(frm)=>{
						if(frm.doc.is_return ==1){
							frm.set_value("is_return_inv","مرتجع-Return")
						}
					}
				})
				"""
			doc.save()
	except:
		pass
def after_install():
	print("+dynamic")
	create_currency_exchange_rate_script()
	create_sales_invoice_script()
	create_invoice_custom_field()
	# create_domain_list()
	# try:
	# 	frappe.db.sql("""delete from tabWorkspace where name in ("HR","Loans","Payroll","Quality","Projects","Support")""")
	# 	frappe.db.commit()
	# 	frappe.db.sql("""delete from tabDocType where module='Loan Management'""")
	# 	frappe.db.commit()
	# 	frappe.db.sql("""delete from `tabModule Def` where name='Loan Management'""")
	# 	frappe.db.commit()
	# 	# frappe.db.sql("""delete from tabDocType where module='Payroll'""")
	# 	# frappe.db.commit()
	# 	frappe.db.sql("""delete from tabDocType where module="Payroll" and name!='Salary Component'""")
	# 	frappe.db.commit()
	# 	# frappe.db.sql("""delete from tabDocType where module='Projects'""")
	# 	# frappe.db.commit()
	# 	# frappe.db.sql("""delete from `tabModule Def` where name='Projects'""")
	# 	# frappe.db.commit()
	# 	print("+del module.text")
	# 	#### after that del them from module
	# 	a_file = open("../apps/erpnext/erpnext/modules.txt", "r")
	# 	lines = a_file.readlines()
	# 	a_file.close()
	# 	new_file = open("../apps/erpnext/erpnext/modules.txt", "w")
	# 	for line in lines:
	# 		if line.strip("\n") !="Loan Management":
	# 			new_file.write(line)
	# 	new_file.close()
	# 	install_uom()
	# except Exception as e:
	# 	print(e)
	# 	pass


def install_uom():
	file_path = "../apps/dynamic/dynamic/MasterData/UnitTypes.json"
	with open(file_path) as f:
		data = json.load(f)
		# print (data)
		for i in data :
			# print (i)
			try:
				frappe.get_doc({
					"doctype":"UOM",
					"uom_name":i.get("code"),
					"english_description":i.get("desc_en"),
					"arabic_description":i.get("desc_ar"),
				}).insert()
				# print (str(i.get("desc_en")))
			except Exception as e:
				pass
				# print (str(e))

def create_domain_list():
	if not frappe.db.exists("Domain", "IFI"):
		dm1 = frappe.new_doc("Domain")
		dm1.domain = 'IFI'
		dm1.insert()

