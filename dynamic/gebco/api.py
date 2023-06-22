from datetime import datetime
import frappe
from frappe import _
from dynamic.gebco.doctype.sales_invocie.stock_settings import caculate_shortage_item
from dynamic.product_bundle.doctype.packed_item.new_packed_item import make_packing_list , get_old_invocie
from dynamic.gebco.doctype.sales_invocie.utils import set_complicated_pundel_list
DOMAINS = frappe.get_active_domains()
import datetime



def validate_packed_item(name):
    invoice_list = frappe.db.sql(f""" 
		select invoice.name 
	     from 
		`tabPacked Item` packed_item 
		inner join `tabProduct Bundle` bundle 
		on bundle.new_item_code = packed_item.item_code 
		INNER join `tabSales Invoice` invoice on packed_item.parent = invoice.name 
		WHERE invoice.name = '{name}'
		group by invoice.name 
		ORDER BY invoice.name
		""")
    if len(invoice_list) > 0 :
        frappe.throw("Packed Item Error")
    if not invoice_list or len(invoice_list) == 0 :
        frappe.msgprint("valid Paked Item")
def validate_sales_invoice(doc,*args,**kwargs):
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
             make_packing_list(doc)
             set_complicated_pundel_list(doc)
             validate_packed_item(doc.name)
        #     caculate_shortage_item(doc.packed_items ,doc.set_warehouse)
    
    if "Majestey" in DOMAINS:
        disable_batch_if_qty_zero(doc)




def disable_batch_if_qty_zero(doc,*args, **kwargs):
    for item in doc.items:
        print("------------------------------- from item grid '%s'"%item.idx)
        if item.get("batch_no"):
            sql = f"""
                update `tabBatch` set disabled = 1 where batch_qty = 0 and name = '{item.batch_no}'
            """
            frappe.db.sql(sql)
            frappe.db.commit()
            
            # batch_doc = frappe.get_doc("Batch",item.get("batch_no"))
            # if batch_doc.batch_qty == 0:
            #     batch_doc.diabled = 1
            #     batch_doc.save()

def validate_delivery_note(doc,*args,**kwargs):
    if 'Gebco' in DOMAINS:
        if doc.maintenance_template:
            m_temp = frappe.get_doc("Maintenance Template",doc.maintenance_template)
            m_temp.delivery_note = doc.name
            m_temp.save()
        if len(doc.packed_items) > 0  : 
            caculate_shortage_item(doc.packed_items ,doc.set_warehouse)
    if 'Terra' in DOMAINS:
        submit_delivery_note(doc)
        minus_delivery_qty_from_reservation(doc,*args,**kwargs)
        check_so_approval(doc)
        recalculate_delivered_qty()
        # if doc.is_return == 1:
        #     #update reservation row where item_code = line_item_code and sales_order=line_sales_order
        #     for line in doc.items:
        #         if line.against_sales_order:
        #             sql = f"""
        #             update `tabReservation Warehouse` AS rsv_warehouse 
        #             INNER JOIN `tabReservation` AS reserve
        #             ON rsv_warehouse.parent=reserve.name AND reserve.`sales_order`='{line.against_sales_order}'
        #             set rsv_warehouse.`reserved_qty`=(rsv_warehouse.`reserved_qty`+ ABS({line.qty})) 
        #             where rsv_warehouse.item='{line.item_code}'
        #             """
        #             frappe.db.sql(sql)
        # if doc.is_return != 1:
            # ..


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
def check_so_approval(doc):
    """
    1 - update approval line qty 
    2- update so line qty 
    """
    #return
    sales_order_approval_name = ""
    total_qty =0
    for item in doc.items:
        if item.get("sales_order_approval"):
            remaing_sql = f"""select remaining_qty from `tabSales Order Approval Item` where parent= '{item.sales_order_approval}' and item_code='{item.item_code}' and warehouse='{item.warehouse}' limit 1"""
            item_remining_qty = frappe.db.sql(remaing_sql,as_dict=1)
            # frappe.errprint(f"==>qty{item.qty} rem {item_remining_qty[0].remaining_qty}")
            if item.qty > item_remining_qty[0].remaining_qty:
                frappe.throw(_("Approval Remaining Qty '%s'"%item_remining_qty[0].remaining_qty))
            #approval_doc = frappe.get_doc("Sales Order Approval",item.get("sales_order_approval"))
            # update approval 
            sql = f"""
             update `tabSales Order Approval Item`
             set remaining_qty = remaining_qty - {item.qty}
             where item_code = '{item.item_code}' and parent = '{item.sales_order_approval}' and warehouse='{item.warehouse}'
            """
            frappe.db.sql(sql)
            frappe.db.commit()
            total_qty += item.qty
           
            sales_order_approval_name = item.sales_order_approval

     # update sales order qty 
    # sql = f"""update `tabSales Order Approval` set total_delivered_qty = total_delivered_qty + {total_qty}"""       
    # frappe.db.sql(sql)
    # frappe.db.commit()
    # so_approval_doc = frappe.get_doc("Sales Order Approval",sales_order_approval_name)
    # total_delived_qty =0
    # #total_delivered_qty
    
    # if so_approval_doc.total_qty == so_approval_doc.total_delivered_qty:
    #     so_approval_doc.status = "Completed"
    #     so_approval_doc.save()
    # elif so_approval_doc.total_qty >so_approval_doc.total_delivered_qty and so_approval_doc.total_delivered_qty != 0:
    #     so_approval_doc.status ="Partial Delivered"
    #     so_approval_doc.save()



            # update sales order qtys

            # so_sql = f"""
            #  update `tabSales Order Item`
            #  set remaining_qty = approved_qty - delivered_qty
            #  where item_code = '{item.item_code}' and parent = '{item.against_sales_order}'
            # """
            # frappe.db.sql(so_sql)
            # frappe.db.commit()
    

def minus_delivery_qty_from_reservation(doc,*args,**kwargs):
    #1-qty deliverd from delivery note
    if not doc.is_return:
        for row in doc.items:
            reserv_data = frappe.db.get_value('Sales Order Item',{'item_code':row.item_code,'parent':row.against_sales_order},['reservation','item_purchase_order','item_warehouse'],as_dict=1)
            reserv_doc = frappe.get_doc('Reservation',reserv_data['reservation'])
            item = frappe.get_doc('Reservation Warehouse',reserv_doc.warehouse[0].name)
            if(item.reserved_qty < row.qty):
                frappe.throw(f'Not Enough Reservation qty for item {row.item_code} for reservation {reserv_data["reservation"]} avail reserved qty {item.reserved_qty}')
            if(row.qty <=  item.reserved_qty):
                if row.qty < item.reserved_qty:
                    reserv_doc.db_set('status','Partial Delivered')
                else:
                    reserv_doc.db_set('status','Closed')
            new_reserved_qty = item.reserved_qty - row.qty
            item.db_set('reserved_qty',new_reserved_qty)
    elif doc.is_return:
        set_reservation_invalid(doc,*args,**kwargs)
        # item.save()
    
@frappe.whitelist()       
def set_reservation_invalid(doc,*args,**kwargs):
    #1-qty deliverd from delivery note
    if  'Terra' in DOMAINS:
        for row in doc.items:
            reserv_data = frappe.db.get_value('Sales Order Item',{'item_code':row.item_code,'parent':row.against_sales_order},['reservation'],as_dict=1)
            reserv_doc = frappe.get_doc('Reservation',reserv_data['reservation'])
            reserv_doc.db_set('status','Invalid')

def validate_purchase_recipt(doc,*args,**kwargs):
    if 'Gebco' in DOMAINS:
        for item in doc.items:
            serial_list = str(item.serial_no).splitlines()
            if item.serial_no:
                if item.serial2:
                    s2_list = item.serial2.splitlines()
                    if len(serial_list) == len(s2_list):
                        for i in range(0,len(serial_list)):
                            sql= """select name from `tabSerial No` where serial2='%s'"""%s2_list[i]
                            res = frappe.db.sql(sql,as_dict=1)
                            if len(res) > 0:
                                frappe.throw(_(f"Serial No {s2_list[i]} Already Exist"))
                            serial_doc = frappe.get_doc("Serial No",serial_list[i])
                            serial_doc.serial2 = s2_list[i]
                            serial_doc.save()
                    else:
                        frappe.throw(_("Serial No list Doest Not Equal Serial2"))


@frappe.whitelist()
def create_installation_request(sales_order):
    sales_order_doc = frappe.get_doc('Sales Order',sales_order)
    installation_request_doc = frappe.new_doc("Installation Request")
    installation_request_doc.sales_order = sales_order
    installation_request_doc.customer = sales_order_doc.customer
    installation_request_doc.customer_name = sales_order_doc.customer_name
    installation_request_doc.total_cars = sales_order_doc.not_requested_cars
    installation_request_doc.posting_date = datetime.datetime.now()
    installation_request_doc.save()
    return installation_request_doc
    


# @frappe.whitelist()
# def get_gebco_items(doc):
#     items = frappe.db.get_list("Item",filters={"item_group","Queclink devices"},fields=['name'],pluck='name')
#     return items



def submit_delivery_note(doc ,*args,**kwargs) :

    if "Terra"  in DOMAINS :
        # validate against terra branches settings  
        user_list = []
        acceess_target = []
       
        user = frappe.session.user
        target_w = False
        if doc.set_warehouse :
            target_w = frappe.get_doc("Warehouse" ,doc.set_warehouse)
        
        if target_w and  not target_w.warehouse_type   :
                #frappe.throw(str("case@ happend"))
            cost_center = frappe.db.sql(f""" 
            SELECT name FROM `tabCost Center` WHERE warehouse ='{doc.set_warehouse}' """ ,as_dict=1)
            if cost_center and len(cost_center) > 0 :
                for obj in cost_center :
                    acceess_target.append(obj.get("name"))
                
        # frappe.errprint(f'centers--->{acceess_target}')
        access_group =    acceess_target 
        if len(access_group) > 0 :
            for access in access_group :
                users = frappe.db.sql(f""" SELECT branch_manager FROM `tabBranch Managers` WHERE parenttype ='Cost Center'
                and parent = '{access}' 
                   """)
                for usr in users :
                    user_list.append(usr[0])
        #validate user access 
        if user not in user_list :
            frappe.throw(f"you can Not Complete this action for Branch  { access_group}")