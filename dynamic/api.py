from datetime import datetime
from warnings import filters
from dynamic.dynamic_accounts.print_format.invoice_tax.invoice_tax import get_invoice_tax_data
import frappe 
from erpnext.accounts.party import get_party_account
from frappe.model.mapper import get_mapped_doc
from frappe.utils import add_days, cint, cstr, flt, get_link_to_form, getdate, nowdate, strip_html
from frappe import _
import codecs
import json
import erpnext
import base64
from frappe.utils.data import add_days, add_months  
#from .product_bundle.doctype.packed_item.packed_item import  make_packing_list
from dynamic.product_bundle.doctype.packed_item.new_packed_item import make_packing_list
from erpnext import get_default_company, get_default_cost_center
from frappe.model.naming import make_autoname
from frappe.utils.user import get_users_with_role
from frappe.utils.background_jobs import enqueue
#from dynamic.product_bundle.doctype.packed_item.packed_item import make_packing_list
from frappe.utils import add_days, nowdate, today
from dynamic.cheques.doctype.cheque.cheque import add_row_cheque_tracks
from dynamic.terra.delivery_note import validate_delivery_notes_sal_ord
from erpnext.stock.doctype.repost_item_valuation.repost_item_valuation import repost_entries
from dynamic.gebco.doctype.sales_invocie.utils import set_complicated_pundel_list
from datetime import date
from dateutil import parser
from six import string_types
from dynamic.ifi.api import validate_payemnt_entry


@frappe.whitelist()
def encode_invoice_data(doc):
    doc = frappe.get_doc("Sales Invoice",doc)
    company = frappe.get_doc("Company",doc.company)
    invoice_data = get_invoice_tax_data(doc.name) or {}
    # print('doc => ' ,doc)
    data_dict = [
        {
            "tagNumber" : 1 ,
            "value" : str(company.company_name or "") 
        },
        {
            "tagNumber" : 2 ,
            "value" : str(company.tax_id or "") 
        },
        {
            "tagNumber" : 3 ,
            "value" : str (doc.posting_date) + " " + str(doc.posting_time) 
        },
        {
            "tagNumber" : 4 ,
            "value" : str((doc.base_rounded_total or doc.base_grand_total )or "") 
        },
        {
            "tagNumber" : 5 ,
            "value" : str(invoice_data.get("total_tax_amount") or "") 
        },
    ]
    total_hex = ""
    for row in data_dict :
        value = row["value"].encode("utf-8").hex()
        if len(row["value"]) > 15:
            value_len = hex(len(row["value"])).replace('0x','')
        else :
            value_len = hex(len(row["value"])).replace('x','')
        tagNumber = hex(row['tagNumber']).replace('x','')

        # value_len = hex(len(row["value"])).replace('0x','')
        # tagNumber = hex(count).replace('0x','')

        total_hex_str = str(tagNumber + value_len+value)

        # hexa_tag = total_hex_str.encode("utf-8")
        total_hex += total_hex_str
        print ("**********************************************")
        print (row["value"])
        print ("value => " , value)
        print ("value_len => " , value_len)
        print ("tagNumber => " , tagNumber)
        print ("total_hex_str => ", total_hex_str)
        # print ("hexa_tag => ", hexa_tag)
    total_hex_b64 = codecs.encode(codecs.decode(total_hex, 'hex'), 'base64').decode('utf-8')
    return total_hex_b64

import frappe
from frappe import _
from .api_hooks.sales_invoice import validate_sales_invocie_to_moyate
from dynamic.dynamic.validation import get_active_domain, validate_sales_invoice
from dynamic.gebco.doctype.sales_invocie.stock_settings import caculate_shortage_item
from dynamic.gebco.doctype.stock_ledger import get_valuation_rate

DOMAINS = frappe.get_active_domains()


@frappe.whitelist()
def validate_active_domains(doc,*args,**kwargs):
    if  'Moyate' in DOMAINS: 
        """   Validate Sales Commition With Moyate """
        validate_sales_invocie_to_moyate(doc)


    if 'Product Bundle' in DOMAINS: 
        """   Update Bundle of Bundles """
        make_packing_list(doc)
        # add child table to sales invoice from utils 

        set_complicated_pundel_list(doc)
    
    if 'Terra' in DOMAINS:
        validate_sales_invoice(doc)
        pass
    if 'Gebco' in DOMAINS:
        if doc.maintenance_template:
            m_temp = frappe.get_doc("Maintenance Template",doc.maintenance_template)
            m_temp.sales_invoice = doc.name
            m_temp.save()
        if doc.maintenance_contract:
            contract_doc = frappe.get_doc("Maintenance Contract",doc.maintenance_contract)
            contract_doc.sales_invoice = doc.name
            contract_doc.save()
        #validate stock amount in packed list 
        #send  packed_items to valid and get Response message with item and shrotage amount and whare house  
        # this fuction validate current srock without looking for other resources    
        if len(doc.packed_items) > 0  and doc.update_stock == 1:
            caculate_shortage_item(doc.packed_items + doc.items  ,doc.set_warehouse)   
    if 'IFI' in DOMAINS:
        # check sINV items valutaion rate
        check_item_valuation_rate(doc)
    
    


def check_item_valuation_rate(doc):
    for item in doc.items:
        value_rate = get_valuation_rate(item.item_code,
        item.warehouse,
        item.parenttype,
        item.parent,
        allow_zero_rate=False,
        currency=erpnext.get_company_currency(doc.company),
        company=doc.company,
        raise_error_if_no_rate=True,
        )
        if(value_rate):
            if(item.rate < value_rate):
                frappe.throw(_(f"Selling Rate cann't Be Less Than Value Rate {value_rate}"))

@frappe.whitelist()
def validate_active_domains_invocie(doc,*args,**kwargs):
    cur_doc  = frappe.get_doc("Sales Invoice" , doc)
    if len(cur_doc.packed_items) > 0  and cur_doc.update_stock == 1:
            caculate_shortage_item(cur_doc.packed_items + cur_doc.items ,cur_doc.set_warehouse)
@frappe.whitelist()
def validate_active_domains_note(doc,*args,**kwargs):
    cur_doc  = frappe.get_doc("Delivery Note" , doc)
   
    if len(cur_doc.packed_items) > 0 :
            caculate_shortage_item(cur_doc.packed_items + cur_doc.items ,cur_doc.set_warehouse)
@frappe.whitelist()
def submit_journal_entry (doc,fun=''):
    if "Cheques" in DOMAINS :
        submit_journal_entry_cheques(doc)

@frappe.whitelist()       
def validate_delivery_note(doc,*args,**kwargs):
    if 'Product Bundle' in DOMAINS: 
        """   Update Bundle of Bundles """
        make_packing_list(doc)
    if 'Gebco' in DOMAINS:
        if doc.maintenance_template:
            m_temp = frappe.get_doc("Maintenance Template",doc.maintenance_template)
            m_temp.delivery_note = doc.name
            m_temp.save()
        if len(doc.packed_items) > 0  :
            make_packing_list(doc)
            set_complicated_pundel_list(doc)
            caculate_shortage_item(doc.packed_items ,doc.set_warehouse)    
    if 'Terra' in DOMAINS:
        # frappe.throw('Validate delivery Note')
        validate_delivery_notes_sal_ord(doc)
        #check_so_approval(doc)



@frappe.whitelist()
def submit_journal_entry_cheques (doc):
    if getattr(doc,"payment_entry",None):
        payment_entry = frappe.get_doc("Payment Entry",doc.payment_entry)
        old_status = payment_entry.cheque_status
        payment_entry.cheque_status = doc.cheque_status
        payment_entry.save()
        add_row_cheque_tracks(doc.payment_entry,doc.cheque_status,old_status)

@frappe.whitelist()
def submit_purchase_invoice(doc , *args , **kwargs) :
    if 'Gebco' in DOMAINS:
          if doc._action == "submit":
            repost_entries()
    if 'Terra' in DOMAINS:
        check_pr_reservation(doc)

    
    #erpnext.stock.doctype.repost_item_valuation.repost_item_valuation.repost_entries
# ---------------- get sales return account ------------------  #
@frappe.whitelist()
def get_sales_return_account():
    company_name = get_default_company()
    company_doc = frappe.get_doc("Company",company_name)
    if company_doc.get("sales_return_account"):
        return company_doc.get("sales_return_account")
    return



# item auto name
def autoname(self,fun=''):
    if 'Terra' in DOMAINS:
        #series = "Tax-Inv-.DD.-.MM.-.YYYY.-.###." if getattr(self,'tax_auth' , 0) else self.naming_series
        self.item_code=generate_item_code(self.item_group)
        self.name = self.item_code


@frappe.whitelist()
def generate_item_code(item_group):
    group_doc = frappe.get_doc("Item Group",item_group)
    group_code = group_doc.code
    if not group_code:
        frappe.msgprint(_("Item Group Doesnt Have Code"))
        return 'false'
    sql = f"""
    select count(*) +1 as 'serial' from `tabitem code serial` where item_group= '{group_doc.name}'
    """
    res = frappe.db.sql(sql,as_dict=1)

    serial = str(group_code or '')+'-' + str(res[0].serial or '')

    return serial


@frappe.whitelist()
def create_new_appointment(source_name, target_doc=None):
    doc = frappe.get_doc("Lead", source_name)
    appointment_doc = frappe.new_doc("Appointment")
    appointment_doc.customer_name = doc.lead_name
    appointment_doc.customer_phone_number = doc.get('phone_no','') 
    appointment_doc.appointment_with = "Lead"
    appointment_doc.party = doc.name
    appointment_doc.customer_email = doc.email_id
    return appointment_doc


from dynamic.gebco.api import validate_purchase_recipt
def submit_purchase_recipt_based_on_active_domains(doc,*args,**kwargs):
    if 'Gebco' in DOMAINS:
        validate_purchase_recipt(doc)
    if 'Terra' in DOMAINS:
        check_email_setting_in_stock_setting(doc)
        #check if PR has Reservation & reserve over warehouse
        check_pr_reservation(doc)

def check_email_setting_in_stock_setting(doc):
    sql = """
    select document,role from `tabEmail Setting`;
    """
    setting_table = frappe.db.sql(sql,as_dict=1)
    if setting_table:
        for row in setting_table:
            if row.document == "Purchase Recipt" and row.role:
                link_str = frappe.utils.get_url_to_form("Purchase Receipt",doc.name)
                msg = f"New Purchase Recipt Created  {link_str}"
                send_mail_by_role(row.role,msg,"Purchase Receipt")
            # if row.document == "Item Re Order" and row.role:
            #     msg = f"New Purchase Recipt Created  {link_str}" 
            # if row.document == "Safty Stock" and row.role:
            #     pass

def check_pr_reservation(doc):
    if doc.doctype == "Purchase Invoice":
        if  doc.update_stock:
            loop_over_doc_items(doc)
    if doc.doctype == 'Purchase Receipt':
        loop_over_doc_items(doc)

def loop_over_doc_items(doc):
    for row in doc.items:
        if(row.purchase_order):
            #get all reservation for this purchase_order wiz this item
            get_po_reservation(row.purchase_order,row.item_code,row.warehouse)


def get_po_reservation(purchase_order,item,target_warehouse):
    reservation_list_sql = f"""SELECT `tabReservation`.name from `tabReservation` WHERE `tabReservation`.status <> 'Invalid'
      AND `tabReservation`.order_source='{purchase_order}' AND `tabReservation`.item_code = '{item}' AND sales_order <> 'Invalid' AND `tabReservation`.warehouse_source = '' """
    data = frappe.db.sql(reservation_list_sql,as_dict=1)
    if data:
        for reservation in data:
            # make reserv over warehouse
            reserv_doc = frappe.get_doc('Reservation',reservation.get('name'))
            oldest_reservation = reserv_doc.reservation_purchase_order[0]
            bin_data = frappe.db.get_value('Bin',{'item_code':item,'warehouse':target_warehouse}
                        ,['name','warehouse','actual_qty','reserved_qty'],as_dict=1)
            reserv_doc.warehouse_source = target_warehouse
            reserv_doc.order_source = ''
            reserv_doc.warehouse = [] #?add row
            row = reserv_doc.append('warehouse', {})
            row.item = item
            row.bin = bin_data.get('name')
            row.warehouse = target_warehouse
            row.qty = oldest_reservation.qty
            row.reserved_qty =  oldest_reservation.reserved_qty
            #! not clear TODO
            row.current_available_qty = bin_data.get('actual_qty') + row.qty - bin_data.get('reserved_qty')
            # row.available_qty_atfer___reservation = bin_data.get('actual_qty') - bin_data.get('reserved_qty')#row.current_available_qty - row.reserved_qty
            reserv_doc.reservation_purchase_order = []
            reserv_doc.save()
            

def validate_material_request(doc,*args,**kwargs):
    sql = """
    select document,role from `tabEmail Setting` where document='Item Re Order';
    """
    setting_table = frappe.db.sql(sql,as_dict=1)
    if len(setting_table) > 0:
        if setting_table[0].role:
            link_str = frappe.utils.get_url_to_form("Material Request",doc.name)
            msg = f" Material Request {link_str} Created Successfully "
            send_mail_by_role(setting_table[0].role,msg,"Item Re Order")
        

def validate_material_request_cost_center(doc,*args,**Kwargs):
    if doc.get("cost_center"):
        for item in doc.get("items"):
            if not item.get("cost_center"):
                item.cost_center = doc.get("cost_center")

def onsave_material_request(doc,*args,**kwargs):
     if "Terra" in DOMAINS:
        validate_material_request_cost_center(doc)
        
import os
# @frappe.whitelist()
def saftey_stock():
    sql = """
    select document,role from `tabEmail Setting` where document='Safty Stock';
    """
    setting_table = frappe.db.sql(sql,as_dict=1)
    if len(setting_table) > 0:
        item_sql = """
            select tb.item_code  ,sum(tb.actual_qty) as 'actual_qty',ti.safety_stock 
            from tabBin tb
            inner join tabItem ti 
            on tb.item_code = ti.name
            group by tb.item_code
            HAVING  sum(tb.actual_qty) > ti.safety_stock 
        """ 
        
        item_list = frappe.db.sql(item_sql,as_dict=1)
        str_list = "This Items Exceed safty stock limit"
        str_list += "("
        for itm in item_list:
            print("aaaaaa",itm.item_code)
            str_list +=" %s , "%itm.item_code
        str_list += ")"
        print("str list",str_list)
        #shotage_string = " This Items Exceed safty stock limit " + lst_str
        
        asd = send_mail_by_role(setting_table[0].role,str_list,"Saftey Stock")
        return asd
        
@frappe.whitelist()
def check_delivery_warehosue(doc_name,item_code,warehouse):
     if not warehouse and item_code:
                purchase_warehouse_list=frappe.db.get_list('Purchase Order Item', filters={
                                    'parent':doc_name,
                                    'item_code':item_code
                                },
                                fields=['warehouse']
                                )
                return purchase_warehouse_list[0].get('warehouse')



# @frappe.whitelist()
def send_mail_by_role(role,msg,subject):
    try:
        recip_list = get_users_with_role(role)
        email_args = {
            "recipients": recip_list,
            "sender": None,
            "subject": subject,
            "message":msg,
            "now": True
        }
        print(" emails =====> ", email_args )

        if not frappe.flags.in_test:
            frappe.enqueue(method=frappe.sendmail, queue="short", timeout=500, is_async=True, **email_args)
        else:
            frappe.sendmail(**email_args)
        return email_args
    except Exception as ex:
        print("exception",str(ex))





@frappe.whitelist()
def check_source_item(self,*args , **kwargs):
    if "Terra" in DOMAINS:
        # sales_order_doc = frappe.get_doc('Sales Order',self)
        for item in self.items:
             #TODO if item has purchase and warehouse show error or both has value
            if (not item.item_warehouse and  not item.item_purchase_order):
                frappe.throw(_(f"Please Select Source As Warehouse Or Purchase Order for Item {item.item_code}"))
            if ( item.item_warehouse and  item.item_purchase_order):
                frappe.throw(_(f"Please Select Just One Source As Warehouse Or Purchase Order for Item {item.item_code} Not Both"))
            if (not item.warehouse and item.item_purchase_order):
                def_warhouse = check_delivery_warehosue(item.item_purchase_order,item.item_code,'')
                item.db_set('warehouse',def_warhouse)
    if 'IFI' in DOMAINS:
        # print('\n\n\n-->in reconslation**')
        update_against_document_in_jv(self)

    
def update_against_document_in_jv(self):
		party_type = "Customer"
		party = self.customer
		party_account = get_party_account(party_type, party=party, company=self.company)
		dr_or_cr = "credit_in_account_currency"
		lst = []
		if self.get("advancess"):
			for d in self.get("advancess"):
				if flt(d.allocated_amount) > 0:
					args = frappe._dict(
						{
							"voucher_type": d.reference_type,
							"voucher_no": d.reference_name,
							"voucher_detail_no": d.reference_row,
							"against_voucher_type": self.doctype,
							"against_voucher": self.name,
							"account": party_account,
							"party_type": party_type,
							"party": party,
							"is_advance": "Yes",
							"dr_or_cr": dr_or_cr,
							"unadjusted_amount": flt(d.advance_amount),
							"allocated_amount": flt(d.allocated_amount),
							"precision": d.precision("advance_amount"),
							"exchange_rate": (
								self.conversion_rate if self.party_account_currency != self.company_currency else 1
							),
							"grand_total": (
								self.base_grand_total
								if self.party_account_currency == self.company_currency
								else self.grand_total
							),
							"outstanding_amount": 0.0, #self.outstanding_amount,
							"difference_account": frappe.db.get_value(
								"Company", self.company, "exchange_gain_loss_account"
							),
							"exchange_gain_loss": flt(d.get("exchange_gain_loss")),
						}
					)
					lst.append(args)

			if lst:
				from dynamic.terra.utils import reconcile_against_document
				reconcile_against_document(lst)

@frappe.whitelist()
def create_reservation_validate(self,*args , **kwargs):
    if "Terra" in DOMAINS:
        check_total_reservation(self)
        add_row_for_reservation(self)
       
def add_row_for_reservation(self):
    # if not self.reservation:
    #! ask if new company will ttake same behavior for warhouse and sales order
    for item in self.items:
        sql = f"""
        select soi.reservation from `tabSales Order` so
        INNER JOIN`tabSales Order Item` soi 
        ON soi.parent = '{self.name}' AND soi.item_code= '{item.item_code}'
        where so.name = '{self.name}'
        """
        sql_reserv = frappe.db.sql(sql)
        if not item.reservation or not len(sql_reserv):
            reserv_doc = frappe.new_doc('Reservation')
            reserv_doc.item_code = item.item_code
            reserv_doc.status = 'Active'
            reserv_doc.valid_from = self.transaction_date
            reserv_doc.reservation_amount = item.qty
            #source in reservation = row.source else slaes_order_source
            reserv_doc.warehouse_source = item.item_warehouse if item.item_warehouse  else "" #self.set_warehouse
            if not reserv_doc.warehouse_source:
                reserv_doc.order_source = item.item_purchase_order if item.item_purchase_order else "" #self.purchase_order
            reserv_doc.save()
            item.db_set('reservation' ,reserv_doc.name )
            item.db_set('reservation_status' ,reserv_doc.status )
            reserv_doc.db_set('sales_order',self.name)
            frappe.db.commit()

def check_total_reservation(self):
    for item in self.items:
        if item.item_warehouse:
            validate_warehouse_stock_reservation(item.item_code,item.item_warehouse,item.qty)
        if item.item_purchase_order:
            validate_purchase_order_reservation(item.item_code,item.item_purchase_order,item.qty)

def validate_warehouse_stock_reservation(item_code,warehouse_source,reservation_amount):
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
				WHERE `tabBin`.warehouse = '{warehouse_source}'
				AND `tabBin`.item_code = '{item_code}'
				AND `tabReservation`.status <> "Invalid"
				""" ,as_dict=1)
	if data and len(data) > 0 :
		if data[0].get("qty") == 0 or float( data[0].get("qty")  or 0 ) < reservation_amount  :
			frappe.throw(_(f""" stock value in warehouse {warehouse_source} = {data[0].get("qty") or 0} 
				and you requires  {reservation_amount} for Item {item_code}  """))
	if  not data or len(data) == 0 :
			frappe.throw(_(f"""no stock value in warehouse {warehouse_source} for item {item_code}  """))
	return data

def validate_purchase_order_reservation(item_code,order_source,reservation_amount):
	order =  frappe.db.sql(f"""                   
		SELECT `tabPurchase Order Item`.name as `name` 
		,`tabPurchase Order Item`.parent,`tabPurchase Order Item`.parenttype as doctype,
		CASE
		WHEN `tabReservation Purchase Order`.reserved_qty > 0 
		then 
		(`tabPurchase Order Item`.qty - `tabPurchase Order Item`.received_qty) - SUM(`tabReservation Purchase Order`.reserved_qty)
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
        AND `tabReservation`.status <> "Invalid"
		where `tabPurchase Order Item`.item_code = '{item_code}'  
		AND `tabPurchase Order Item`.parent = '{order_source}' 
		""",as_dict=1)
	
	if order and len(order) > 0 :
		if order[0].get("parent") and float(order[0].get("qty")) ==  0 :
			frappe.throw(_(f"  Purchase Order {order_source} don't have {item_code} Qty and you requires  {reservation_amount}" ))
		if not order[0].get("parent") :
			frappe.throw(_(f"  Purchase Order {order_source} don't have item {item_code}" ))	
	if not order or  len(order) == 0 :
		frappe.throw(_(f"Invalid Purchase Order {order_source} don't have item {item_code}"))

@frappe.whitelist()
def cancel_reservation(self,*args , **kwargs):
    if "Terra" in DOMAINS:
        for item in self.items:
            if(item.reservation):
                frappe.db.set_value('Reservation',item.reservation,'status','Invalid')




@frappe.whitelist()
def validate_sales_order_reservation_status():

    # 1- get conf
    reservation_conf = """
    select * from `tabReservation Child`
    """
    conf_result = frappe.db.sql(reservation_conf,as_dict=1)

    # 2- get all sales order with reservation_status = 'Active'
    sql = """
        select 
            tso.name
            ,tsoi.name as 'childname'
            ,tsoi.reservation 
            ,tsoi.reservation_status
            ,tso.advance_paid
            ,tso.base_grand_total
            ,DATEDIFF(CURDATE(),tso.creation) as 'diff' 
            from 
            `tabSales Order Item` tsoi
            inner join `tabSales Order` tso 
            on tso.name = tsoi .parent 
            where tsoi.reservation  is not null and tsoi.reservation_status ='Active'
        """
    sales_order_result = frappe.db.sql(sql,as_dict=1)

    # loop throgth conf and update sales order that achive criteria
    for c in conf_result:
        for s in sales_order_result:
            if s.diff >= float(c.days or 0) and ((float(s.advance_paid or 0) / s.base_grand_total) *100 < float(c.percent or 0) or c.percent==0):
                #sales_order = frappe.get_doc("Sales Order",s.name)
                reserv_doc = frappe.get_doc("Reservation",s.reservation)
                reserv_doc.status = "Closed"
                reserv_doc.closing_date = nowdate()
                reserv_doc.save()
                # sales_order.reservation_status = "Closed"
                # sales_order.save()
                sql = f""" update `tabSales Order Item` set  reservation_status='Closed' where name='{s.childname}'"""
                frappe.db.sql(sql)
                frappe.db.commit()
                





@frappe.whitelist()
def get_active_domains():
    return frappe.get_active_domains()
    
@frappe.whitelist()
def submit_payment(doc,*args,**kwargs):
     if "Terra" in DOMAINS:
          submit_payment_for_terra(doc)

@frappe.whitelist()
def validate_paymentrntry(doc , *args,**kwargs) :
    if "IFI" in DOMAINS :
        validate_payemnt_entry(doc)
@frappe.whitelist()
def update_paymentrntry(doc, *args,**kwargs) :
    if "Cheques" in DOMAINS :
        #validate party account with part type 
       
        if doc.endorse_cheque ==1 :    
            if doc.endorsed_party_type and doc.endorsed_party_account :
                party_type_account_type = frappe.get_doc("Party Type" , doc.endorsed_party_type).account_type
                part_account_type  = frappe.get_doc("Account" ,doc.endorsed_party_account ).account_type
                if party_type_account_type  !=  part_account_type :
                    party_account = get_party_account(doc.endorsed_party_name, party=doc.endorsed_party_type, company=doc.company)
                    # frappe.throw(f"Acoount {party_account}")

                    if party_account :
                        doc.endorsed_party_account = party_account
                    if not party_account :
                        if doc.endorsed_party_type == "Customer" :
                            doc.endorsed_party_account = frappe.get_doc("Company" , doc.company).default_receivable_account
                        if doc.endorsed_party_type == "Supplier" :
                             doc.endorsed_party_account = frappe.get_doc("Company" , doc.company).default_payable_account
                    
                    frappe.db.commit()
                    #  frappe.throw(_(f" Endorsed Party Account type is {party_type_account_type} and party type {doc.endorsed_party_type} "))
                    #get defalu party type account
@frappe.whitelist()
def submit_payment_for_terra(doc , *args ,**kwargs):
    if doc.references and len (doc.references) > 0 :
        for ref in doc.references :
            if ref.reference_doctype in ["Sales Order" , "Sales Invoice" ]  :
                
                out_stand = frappe.db.sql(f"""SELECT 
                b.total_amount - SUM(b.allocated_amount)  AS out_stand FROM 
                `tabPayment Entry Reference` b
                Inner Join `tabPayment Entry` a 
                ON a.name = b.parent
                WHERE b.reference_doctype ="{ref.reference_doctype}" AND 
                b.reference_name ='{ref.reference_name}' AND a.docstatus =1
                """,as_dict =1)  
                # update sales order allocated amount if payment againest sales order 
                if ref.reference_doctype == "Sales Order" :
                    if out_stand and out_stand[0].get("out_stand") : 
                        frappe.db.sql(f""" UPDATE `tabSales Order` SET 
                        outstanding_amount ={ out_stand[0].get("out_stand")} 
                        WHERE name = "{ref.reference_name}" """)
                        frappe.db.commit()
                
                  # update sales order allocated amount if payment againest sales invoice 
                if ref.reference_doctype == "Sales Invoice" :
                    #get invoice total 
                    invoice_total = frappe.db.get_value("Sales Invoice" , ref.reference_name ,"total")
                   
                    sales_invoice = frappe.get_doc("Sales Invoice" , ref.reference_name )
                    orders =[]
                    for line  in sales_invoice.items :
                        if line.sales_order not in orders :
                            # frappe.throw(str(line.sales_order))
                            order_amount = frappe.db.sql(f"""SELECT SUM(b.amount) AS amount 
                                    FROM 
                                    `tabSales Invoice Item` b 
                                    inner join `tabSales Invoice` a 
                                    ON a.name = b.parent
                                    WHERE  
                              b.sales_order  ="{line.sales_order}" 
                              AND a.docstatus =1""",as_dict = 1)
                            orders.append(line.sales_order)
                            if len(orders) > 1 :
                                frappe.throw(""" Sales Invocie Line Have To many orders """)
                            if len(order_amount) >  0 and order_amount[0].get("amount") :
                                # oreder_perecent = float(order_amount[0].get("amount")) / float(invoice_total or 0)
                                # order_amount = line.amount * oreder_perecent
                                amount =out_stand[0].get("out_stand")
                                order_name = line.sales_order
                                frappe.db.sql(""" UPDATE `tabSales Order`  SET  outstanding_amount = %d 
                                 WHERE name = '%s'  """%(amount , order_name))
                                frappe.db.commit()


                                #frappe.throw(str(oreder_perecent))
                    



@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_purchase_order(doctype, txt, searchfield, start, page_len, filters):
    if  filters and filters.get("item_code"):
        return frappe.db.sql(
            f"""select po.parent from `tabPurchase Order Item` po
                where po.item_code = '{filters.get("item_code")}' AND IFNULL(po.received_qty,0) < po.qty
                """
        )
    return ()


@frappe.whitelist()
def change_row_after_submit(doc , *args ,**kwargs):
    if('Terra' in DOMAINS):
        """
        1-get all reservation list for sales order
        2-then update qty if this reservation still exist 
        3-set status as invalid for reserv if  row deleted
        4- create new reservation if new row added
        """
        sql_reserv = f"""
            select name from tabReservation tr where sales_order ='{doc.name}'
        """
        sql_reserv = frappe.db.sql(sql_reserv)
        sql_reserv_list = [l[0] for l in sql_reserv]
        for row in doc.items:
            if(row.reservation and row.reservation_status == 'Active'):
                if(row.get('item_purchase_order')):
                    sql = f"""
                        UPDATE `tabReservation Purchase Order` trpo
                        SET trpo.reserved_qty  = {row.qty}
                        WHERE trpo.parent='{row.reservation}' AND Item='{row.item_code}';
                    """
                    frappe.db.sql(sql)
                if row.get('item_warehouse'):
                    sql = f"""
                        UPDATE `tabReservation Warehouse` trw
                        SET trw.reserved_qty  = {row.qty}
                        WHERE trw.parent='{row.reservation}' AND Item='{row.item_code}';
                    """
                    frappe.db.sql(sql)

                if row.reservation in sql_reserv_list:
                    sql_reserv_list.remove(row.reservation)
            # if(not row.reservation):
            #     #**check if have ware house or purchase invoice
            #     check_source_item(doc)
            #     #**create reservation
            #     add_row_for_reservation(doc)
        else:
            if len(sql_reserv_list):
                for reservation in sql_reserv_list:
                    frappe.db.set_value('Reservation',reservation,{'status':'Invalid'})
    


#add Whats App Message send Button 
@frappe.whitelist()
def validate_whatsApp(*args , **kwargs) :
      if  'Moyate' in DOMAINS: 
        """   Validate Sales Commition With Moyate """
        return True
@frappe.whitelist()
def validate_terra_domain(*args , **kwargs) :
      if  'Terra' in DOMAINS: 
        """   Validate Tera ui customization  """
        return True
@frappe.whitelist()
def validate_whats_app_settings(data , *args ,**kwargs) :
    json_data = json.loads(data)
    #get_active_profile 
    profile = frappe.db.sql(""" SELECT name from `tabWhatsApp`  WHERE status = 'Active' """ ,as_dict =1)
    if len(profile) == 0 :
        frappe.throw("No Active profile")
    if len(profile) > 0 :
        for i in json_data :
            msg = frappe.new_doc("Whats App Message")
            msg.customer = frappe.get_doc("Customer" ,i.get("name")).name
            msg.fromm = profile[-1].get("name")
            msg.save()
            # frappe.throw(i.get("name"))





@frappe.whitelist()
def modeofpaymentautoname(self,fun=''):
    if "Terra" in DOMAINS:
        mode_of_payment = frappe.get_doc("Mode of Payment",self.mode_of_payment)
        if mode_of_payment.get("naming"):
            todays_date = date.today()
            year = todays_date.year
            id = create_naming_reord(mode_of_payment.get("naming"))
            nameingstr = mode_of_payment.get("naming")
            nameingstr = nameingstr.replace(".YYYY.",str(year))
            self.name = nameingstr + str(id)
            



def create_naming_reord(series):
    doc= frappe.new_doc("Mode OF PAYMENT NAMING")
    doc.mode_of_payment_series = series
    doc.save()

    sql = f"""select count(*) as 'c' from `tabMode OF PAYMENT NAMING` WHERE mode_of_payment_series = '{series}'"""
    last_id = frappe.db.sql(sql,as_dict=1)
    id = int(last_id[0].get("c")) 
    return id    
@frappe.whitelist()           
def submit_stock_entry(doc ,*args,**kwargs) :

    if "Terra"  in DOMAINS :
        # validate against terra branches settings  
        user_list = []
        acceess_target = []
        acccess_source = []
        target_types = ["Material Issue" , "Material Transfer" ,"Send to Subcontractor"]
        recive_types = ["Material Receipt" , "Material Transfer"]
        user = frappe.session.user
        target_w = False
        source_w = False
        if doc.from_warehouse :
            target_w = frappe.get_doc("Warehouse" ,doc.from_warehouse)
        if doc.to_warehouse:
            source_w = frappe.get_doc("Warehouse" ,doc.to_warehouse)
        entry_type = frappe.get_doc("Stock Entry Type" ,doc.stock_entry_type).purpose
        
        if target_w and entry_type in target_types and  not target_w.warehouse_type   :
                # frappe.throw(str("case@ happend"))
                cost_center = frappe.db.sql(f""" SELECT name FROM `tabCost Center` WHERE warehouse ='{doc.from_warehouse}' """ ,as_dict=1)
                if cost_center and len(cost_center) > 0 :
                    for obj in cost_center :
                        acceess_target.append(obj.get("name"))
                
        if source_w and  entry_type in recive_types and not  source_w.warehouse_type:
                cost_center = frappe.db.sql(f""" SELECT name FROM `tabCost Center` WHERE warehouse ='{doc.to_warehouse}' """ ,as_dict=1)
                if cost_center and len(cost_center) > 0 :
                    for obj in cost_center :
                         acccess_source.append(obj.get("name"))
        access_group =    acceess_target +  acccess_source 
        if len(access_group) > 0 :
            for access in access_group :
                # frappe.throw(str(access))
                users = frappe.db.sql(f""" SELECT branch_manager FROM `tabBranch Managers` WHERE parenttype ='Cost Center'
                and parent = '{access}' 
                   """)
                # frappe.throw(str(users))
                for usr in users :
                    user_list.append(usr[0])
            
       
        #validate user access 
        if user not in user_list :
            frappe.throw(f"you can Not Complete this action for Branch  { access_group}")
       
            
@frappe.whitelist()           
def submit_purchase_recipt(doc ,*args,**kwargs) :

    if "Terra"  in DOMAINS :
        # validate against terra branches settings  
        user_list = []
        acceess_target = []
        acccess_source = []
        # target_types = ["Material Issue" , "Material Transfer" ,"Send to Subcontractor"]
        # recive_types = ["Material Receipt" , "Material Transfer"]
        user = frappe.session.user
        target_w = False
        source_w = False
        if doc.set_warehouse :
            target_w = frappe.get_doc("Warehouse" ,doc.set_warehouse)
        # if doc.to_warehouse:
        #     source_w = frappe.get_doc("Warehouse" ,doc.set_warehouse)
        # entry_type = frappe.get_doc("Stock Entry Type" ,doc.stock_entry_type).purpose
        
        if target_w and  not target_w.warehouse_type   :
                #frappe.throw(str("case@ happend"))
            cost_center = frappe.db.sql(f""" SELECT name FROM `tabCost Center` WHERE warehouse ='{doc.set_warehouse}' """ ,as_dict=1)
            if cost_center and len(cost_center) > 0 :
                for obj in cost_center :
                    acceess_target.append(obj.get("name"))
                
        
        access_group =  acceess_target 
        if len(access_group) > 0 :
            for access in access_group :
                # frappe.throw(str(access))
                users = frappe.db.sql(f""" SELECT branch_manager FROM `tabBranch Managers` WHERE parenttype ='Cost Center'
                and parent = '{access}' 
                   """)
                # frappe.throw(str(users))
                for usr in users :
                    user_list.append(usr[0])
            
       
        #validate user access 
        if user not in user_list :
            frappe.throw(f"you can Not Complete this action for Branch  { access_group}")

@frappe.whitelist()
def validate_mode_of_payment_naming(old_naming=None,mode_of_payment=None,*args, **kwargs):
    if not mode_of_payment or not old_naming:
        return True
    doc = frappe.get_doc("Mode of Payment",mode_of_payment)
    if doc.naming == old_naming:
        return True
    return False

from dynamic.dynamic.doctype.sales_person_commetion.sales_person_commetion import  update_month_previous_logs_for_person

@frappe.whitelist()
def validate_active_domains_cancel(doc ,*args,**kwargs):
    if  'Moyate' in DOMAINS: 
        # Clear Invoice Commision Amount 
        #1 - remove commition log 
        # 2 -update old logs  

        #get invocie log  
        invoice_log = frappe.db.sql(f""" SELECT name FROM `tabSales Person Commetion` WHERE invocie = '{doc.name}'""" ,as_dict=1)
        # frappe.throw(str(invoice_log))
        if invoice_log and len(invoice_log) > 0 :
            for l in invoice_log :
                log = frappe.get_doc("Sales Person Commetion" , l.get("name"))
                
                first_day  = log.from_date
                last_day = log.to_date 
                person = log.sales_person
                item_group = log.item__group
                # log.remove_raw()
                frappe.db.sql(f""" DELETE FROM `tabSales Person Commetion` WHERE name = '{l.get("name")}'""")
                frappe.db.commit()
                update_month_previous_logs_for_person(first_day , last_day , item_group ,person  )


     
@frappe.whitelist()           
def before_save(doc ,*args,**kwargs) :
    if doc.items:
        for row in doc.items:
            if row.get("purchase_order"):
                recevied_qty = frappe.db.get_value("Purchase Order Item",{
                    "parent":row.get("purchase_order"),
                    "item_code":row.get("item_code")
                },"received_qty"
                )
                row.actual_received_qty = recevied_qty
        # first_day = datetime.today().replace(day=1)
        # last_day = add_days(add_months(first_day, 1),-1) 

        # sql = f"""
        #             select
        #                 name ,
        #                 sales_person ,
        #                 item__group ,
        #                 commission_template ,
        #                 commission_amount ,
        #                 invoice_qty ,
        #                 from_date ,
        #                 to_date
        #             from
        #                 `tabSales Person Commetion` t1
        #             where
        #                 t1.name = (
        #                 select
        #                     t2.name
        #                 from
        #                     `tabSales Person Commetion` t2
        #                 where
        #                     t2.from_date = date('{first_day}')
        #                     and t2.to_date = date('{last_day}')
        #                     and t1.sales_person = t2.sales_person
        #                     and t1.item__group = t2.item__group
        #                     and t1.commission_template = t2.commission_template
        #                 ORDER BY
        #                     t2.sales_person ,
        #                     t2.item__group ,
        #                     t2.commission_template ,
        #                     t2.creation DESC
        #                 limit 1
        #             )
        #             ORDER BY
        #                 t1.sales_person ,
        #                 t1.item__group ,
        #                 t1.commission_template ,
        #                     t1.creation DESC
        #     """
        # logs = frappe.db.sql(sql,as_dict=1) or []
    
        # for row in logs :
        #     doc = frappe.get_doc("Sales Person Commetion" , row.name)
        #     doc.save()
@frappe.whitelist()
def get_item_price(item_code,price_list):
    sql = f"select price_list_rate from `tabItem Price` where price_list = '{price_list}' and item_code='{item_code}'"
    res = frappe.db.sql(sql,as_dict=1)
    print("----------------------------------------------",len(res))
    if len(res) >0:
        return res[0].get("price_list_rate") or 0
    return 0



@frappe.whitelist()
def add_cost_center_to_asset(doc,*args, **kwargs):
    for item in doc.assets:
        asset = frappe.get_doc("Asset",item.asset)
        if item.get("cost_center"):
            if item.get("cost_center") !=asset.get("cost_center") : 
                sql = f""" update tabAsset set cost_center = '{item.cost_center}' where name = '{asset.name}'"""
                frappe.db.sql(sql)
                frappe.db.commit()



@frappe.whitelist()
def validate_stock_entry(doc,*args,**kwargs):
    if isinstance(doc, str)  :
        data = json.loads(doc)
        if data.get("name") :
             doc = frappe.get_doc("Stock Entry" , data.get('name'))
        
        else :
            doc =False 
            target = data.get("outgoing_stock_entry")
            return target

    if  'Terra' in DOMAINS:
        if doc != False :
            if doc.outgoing_stock_entry :
                target =  frappe.db.get_value('Stock Entry', f'{doc.outgoing_stock_entry}', 'ds_warehouse')
                doc.to_warehouse = target
                return target

    # Add vana validate 

    if 'Vana' in DOMAINS :
        caculate_vana_price(doc)
#caculate vana stock entry sales price 
#    
def caculate_vana_price(doc): 
    total_sales = 0
    for item in doc.items : 
        if float(item.get("sales_price") or  0)  > 0 :
            item.total_sales_price = item.qty * item.sales_price 
            total_sales += float(item.total_sales_price or 0 )
    doc.total_entry_sales_price = total_sales
@frappe.whitelist()
def create_new_appointment_ifi(source_name, target_doc=None):
    doc = frappe.get_doc("Lead", source_name)
    appointment_doc = frappe.new_doc("Appointment")
    appointment_doc.customer_name = doc.lead_name
    appointment_doc.customer_phone_number = doc.get('phone_no1','') 
    appointment_doc.appointment_with = "Lead"
    appointment_doc.party = doc.name
    appointment_doc.customer_email = doc.email_id
    return appointment_doc


from erpnext import get_company_currency, get_default_company

@frappe.whitelist()
def calculate_orderd_qty(doc,*args , **kwargs) :
    if 'IFI' in DOMAINS:
       
        for item_o in doc.items:
            if item_o.sales_order : 
                # calculate_orderd_qty(item.sales_order)
                sales_order = frappe.get_doc("Sales Order" ,item_o.sales_order)
                order_qty , sales_qty = 0  , 0 
                for item in sales_order.items :
                    sales_qty = sales_qty + float(item.qty)
                    order_qty = order_qty + float(item.ordered_qty)
                per_orderd = (order_qty / sales_qty) *100
                
                sales_order.per_orderd = per_orderd

                sales_order.save()
               
                frappe.db.sql(f""" 
                UPDATE `tabSales Order` SET per_orderd={per_orderd} 
                WHERE name ='{item_o.sales_order}'
                
                """)
                frappe.db.commit()
            # frappe.throw(f"{sales_order.per_orderd}")
            

@frappe.whitelist()
def add_crean_in_taxes(doc,*args,**kwargs):
    if 'IFI' in DOMAINS:
        total = 0
        if(doc.crean=='Yes' and doc.crean_amount >0):
            if len(doc.taxes):
                for row in doc.taxes:
                    total  = row.total
        crean_account = frappe.db.get_value('Company',doc.company,"crean_income_account")
        if(crean_account):
            if doc.doctype == "Quotation" and crean_account:
                company = get_default_company()
                doc.append("taxes",{
                    "charge_type":"Actual",
                    "account_head":crean_account,
                    "tax_amount":doc.crean_amount,
                    "total":doc.crean_amount + total,
                    "description":crean_account
                })
                total = doc.crean_amount + total
                doc.total_taxes_and_charges = doc.crean_amount + total
            elif  doc.doctype == "Purchase Order" and crean_account:
                doc.append("taxes",{
                    "charge_type":"Actual",
                    "account_head":crean_account,
                    "tax_amount":doc.crean_amount,
                    "total":doc.crean_amount + total,		
                    "tax_amount_after_discount_amount":doc.crean_amount,		
                    "description":crean_account,
                    "category":"Total",
                    "add_deduct_tax":"Add",
                })
                total = doc.crean_amount + total
                doc.total_taxes_and_charges =  total
            doc.run_method("calculate_taxes_and_totals")
        if(not crean_account):
            frappe.msgprint(_("Company Has No Crane Account"))
       
@frappe.whitelist()    
def check_crean_amount_after_mapped_doc(doc,*args,**kwargs):
    if 'IFI' in DOMAINS:
        if(doc.crean=='Yes' and doc.crean_amount >0):
            crean_account,cost_center = frappe.db.get_value('Company',doc.company,["crean_income_account","cost_center"])
            if(crean_account):
                flage_crean_tax = True
                total = 0
                if len(doc.taxes):
                    for row in doc.taxes:
                        total = row.total
                        if row.account_head == crean_account:
                            row.tax_amount = doc.crean_amount
                            row.total =  row.total
                            flage_crean_tax = False
                    else:
                        if  flage_crean_tax and  doc.doctype == "Sales Order":
                            doc.append("taxes",{
                            "charge_type":"Actual",
                            "account_head":crean_account,
                            "tax_amount":doc.crean_amount,
                            "total":doc.crean_amount + total,
                            "description":crean_account
                        })
                        elif  flage_crean_tax and  doc.doctype == "Sales Invoice":
                            doc.append("taxes",{
                            "charge_type":"Actual",
                            "account_head":crean_account,
                            "tax_amount":doc.crean_amount,
                            "total":doc.crean_amount + total,
                            "description":crean_account,
                            "cost_center":cost_center,
                        })
                        elif flage_crean_tax and  doc.doctype == "Purchase Invoice":
                            doc.append("taxes",{
                            "charge_type":"Actual",
                            "account_head":crean_account,
                            "tax_amount":doc.crean_amount,
                            "total":doc.crean_amount + total,
                            "description":crean_account,
                            "category":"Total",
                            "add_deduct_tax":"Add",
                            "cost_center":cost_center,
                        })
                    doc.total_taxes_and_charges = doc.crean_amount + total
            doc.run_method("calculate_taxes_and_totals")
            if(not crean_account):
                frappe.msgprint(_("Company Has No Crane Account"))
                 



@frappe.whitelist()    
def check_crean_amount_after_mapped_doc_pi(doc,*args,**kwargs):
    if 'IFI' in DOMAINS:
        if(doc.crean=='Yes' and doc.crean_amount >0):
            crean_account = frappe.db.get_value('Company',doc.company,"crean_income_account")
            if(crean_account):
                flage_crean_tax = True
                total = 0
                if len(doc.taxes):
                    for row in doc.taxes:
                        total = row.total
                        # amount += row.tax_amount
                        if row.account_head == crean_account:
                            row.tax_amount = doc.crean_amount
                            flage_crean_tax = False
                    else:
                        if  flage_crean_tax:
                            doc.append("taxes",{
                            "charge_type":"Actual",
                            "account_head":crean_account,
                            "tax_amount":doc.crean_amount,
                            "total":doc.crean_amount + total,
                            "description":crean_account,
                            "category":"Total",
                            "add_deduct_tax":"Add",
                        })
            doc.run_method("calculate_taxes_and_totals")
            if(not crean_account):
                frappe.msgprint(_("Company Has No Crane Account"))

@frappe.whitelist()   
def onsave_account_settings(doc,*args,**kwargs):
    print("from save function in hook +++++++++++++++++++++++++++++++++++++++++++++++++")
    if 'Merge Entries' in DOMAINS:
        x = "merge_entries=True"
        y = "merge_entries=False"
        if  doc.merge_entries:
            with open("../apps/erpnext/erpnext/accounts/general_ledger.py", 'r') as file:
                data = file.read()
                data = data.replace(x, y)
            with open("../apps/erpnext/erpnext/accounts/general_ledger.py", 'w') as file:
                file.write(data)
        else:
            with open("../apps/erpnext/erpnext/accounts/general_ledger.py", 'r') as file:
                data = file.read()
                data = data.replace(y,x)
            with open("../apps/erpnext/erpnext/accounts/general_ledger.py", 'w') as file:
                file.write(data)





def lead_before_insert(doc,fun=''):
    active_domains = frappe.get_active_domains()
    if "Elevana" in active_domains :
        from dynamic.elevana.api import elevana_lead_before_insert
        elevana_lead_before_insert(doc,fun)


        
@frappe.whitelist()  
def recalculate_delivered_qty():
    sql = """ select name from `tabSales Order Approval` where status not in ('Draft','Cancelled','Completed')"""
    data = frappe.db.sql(sql,as_dict=1)
    for d in data:
        doc = frappe.get_doc("Sales Order Approval",d.name)
        total_delivered_qty = 0
        for item in doc.items:
            delivered_qty = item.approved_qty - item.remaining_qty
            total_delivered_qty += delivered_qty
        # update delivered qty
        update_sql = f""" update `tabSales Order Approval` set total_delivered_qty='{total_delivered_qty}' where name='{d.name}'"""
        frappe.db.sql(update_sql)
        frappe.db.commit()



    # updae status
    res = frappe.db.sql("""select name,total_delivered_qty,total_qty from `tabSales Order Approval` where status not in ('Draft','Cancelled','Completed') """,as_dict=1)
    for r in res:
        update_status_sql = ""
        if  float(r.total_delivered_qty or 0) == 0:
            print("from delivered if")
            update_status_sql  = f""" update `tabSales Order Approval` set status='To Deliver' where name='{r.name}'"""
        elif  r.total_qty == r.total_delivered_qty and r.total_delivered_qty !=0:
            print("from completed if")
            update_status_sql  = f""" update `tabSales Order Approval` set status='Completed' where name='{r.name}'"""
        elif r.total_delivered_qty < r.total_qty and r.total_delivered_qty !=0:
            update_status_sql  = f""" update `tabSales Order Approval` set status='Partial Delivered' where name='{r.name}' """
        
        frappe.db.sql(update_status_sql)
        frappe.db.commit()
    return {"status":"success"}




@frappe.whitelist()
def get_hijri_date(posting_date):
    from hijri_converter import Hijri, Gregorian
    hijri_date = str(Gregorian.fromdate(parser.parse(str(posting_date)).date()).to_hijri())
    hijri_date = parser.parse(str(hijri_date)).date().strftime("%d / %m / %Y")
    return hijri_date

@frappe.whitelist()
def get_street_address_html(party_type, party):
    address_list = frappe.db.sql(
        """
        SELECT
            link.parent
        FROM
            `tabDynamic Link` link,
            `tabAddress` address
        WHERE
            link.parenttype = "Address"
                AND link.link_name = %(party)s
        ORDER BY
            address.address_type="Postal" DESC,
            address.address_type="Billing" DESC
        LIMIT 1
    """,
        {"party": party},
        as_dict=True,
    )
    street_address = city_state = ""
    if address_list:
        supplier_address = address_list[0]["parent"]
        doc = frappe.get_doc("Address", supplier_address)
        if doc.address_line2:
            street_address = "First address :" +doc.address_line1 + " ,Second address :" + doc.address_line2 
        else:
            street_address = doc.address_line1 

        city_state = " City: "+ doc.city + ", " if doc.city else ""
        city_state = city_state + doc.state + " " if doc.state else city_state
        city_state = city_state + doc.pincode if doc.pincode else city_state
        city_state += ""
    return street_address + ',' + city_state

@frappe.whitelist()
def get_party_address(party_type, party):
    address_list = frappe.db.sql(
        """
        SELECT
            link.parent
        FROM
            `tabDynamic Link` link,
            `tabAddress` address
        WHERE
            link.parenttype = "Address"
                AND link.link_name = %(party)s
                AND link.link_doctype = %(party_type)s
        ORDER BY
            address.address_type="Postal" DESC,
            address.address_type="Billing" DESC
        LIMIT 1
    """,
        {"party": party,"party_type":party_type},
        as_dict=True,
    )
    street_address = city_state = ""
    if address_list:
        supplier_address = address_list[0]["parent"]
        doc = frappe.get_doc("Address", supplier_address)
        if doc.address_line2:
            street_address = "First address :" +doc.address_line1 + " ,Second address :" + doc.address_line2 
        else:
            street_address = doc.address_line1 

        city_state = " City: "+ doc.city + ", " if doc.city else ""
        city_state = city_state + doc.state + " " if doc.state else city_state
        city_state = city_state + doc.pincode if doc.pincode else city_state
        city_state += ""
    return street_address + ',' + city_state





