from erpnext.accounts.doctype.account.account import get_account_currency
import frappe

from frappe.utils import add_days, nowdate, today
from dynamic.terra.doctype.payment_entry.payment_entry import get_party_details
from frappe.model.mapper import get_mapped_doc
from frappe.model.utils import get_fetch_values
from frappe.utils import add_days, cint, cstr, flt, get_link_to_form, getdate, nowdate, strip_html
from six import string_types
from frappe.utils import now

Domains = frappe.get_active_domains()

@frappe.whitelist()
def get_iem_sub_uom(item_code,uom,qty):
    item  = frappe.get_doc("Item",item_code)
    # if len(item.uoms) >=1:
    #     if item.uoms[1].uom == uom:
    #         return {
    #         "sub_uom":item.uoms[1].uom,
    #         "sub_uom_conversation_factor":item.uoms[1].conversion_factor,
    #         "qty_as_per_sub_uom": qty
    #     }
    #     return {
    #         "sub_uom":item.uoms[1].uom,
    #         "sub_uom_conversation_factor":item.uoms[1].conversion_factor,
    #         "qty_as_per_sub_uom": float(qty or 0) / float(item.uoms[1].conversion_factor or 0)
    #     }
    # return {
    #         "sub_uom":"",
    #         "sub_uom_conversation_factor":0,
    #         "qty_as_per_sub_uom": 0
    #     }
    for u in item.uoms:
        if u.is_sub_uom:
            if u.uom !=uom:
                return {
                    "sub_uom":u.uom,
                    "sub_uom_conversation_factor":u.conversion_factor,
                    "qty_as_per_sub_uom": float(qty or 0) / float(u.conversion_factor or 0)
                }

            if u.uom == uom :
                return {
                    "sub_uom":u.uom,
                    "sub_uom_conversation_factor":u.conversion_factor,
                    "qty_as_per_sub_uom": qty
                }

    return {
            "sub_uom":"",
            "sub_uom_conversation_factor":0,
            "qty_as_per_sub_uom": 0
        }



# material request type ------------> purchase
# validate if no item   ------------> validation error 
@frappe.whitelist()
def create_sales_order_from_opportunity(source_name, target_doc=None):
    source_doc = frappe.get_doc("Opportunity",source_name)
    doc = frappe.new_doc("Sales Order")
    if source_doc.opportunity_from == "Customer":
        doc.customer = source_doc.party_name
        doc.opportunity = source_doc.name
        doc.source = source_doc.source
    if len(source_doc.items)> 0:
        for item in source_doc.items:
            item_doc = frappe.get_doc("Item",item.item_code)
            doc.append("items",{
                "item_code"     : item.item_code,
                "qty"           : item.qty,
                "item_name"     : item.item_name,
                "description"   : item.item_name,
                "uom"           : item_doc.stock_uom,
                "stock_uom"     : item_doc.stock_uom
            })

    return doc

@frappe.whitelist()
def create_material_request_from_opportunity(source_name, target_doc=None):
    source_doc = frappe.get_doc("Opportunity",source_name)
    doc = frappe.new_doc("Material Request")
    doc.purpose = "Purchase"
    doc.customer_name = source_doc.customer_name if source_doc.customer_name else ''
    doc.opportunity = source_doc.name  
    if len(source_doc.items)> 0:
        for item in source_doc.items:
            item_doc = frappe.get_doc("Item",item.item_code)
            doc.append("items",{
                "item_code"     : item.item_code,
                "qty"           : item.qty,
                "item_name"     : item.item_name,
                "description"   : item.item_name,
                "uom"           : item_doc.stock_uom,
                "stock_uom"     : item_doc.stock_uom,
                "schedule_date" : today()
            })
    return doc




@frappe.whitelist()
def get_quotation_item(quotation,*args,**Kwargs):
    doc = frappe.get_doc("Quotation",quotation)
    return doc.items
    
@frappe.whitelist()
def get_payment_entry_quotation(source_name):
    qutation_doc = frappe.get_doc('Quotation',source_name)

    party_type = qutation_doc.quotation_to
    party = qutation_doc.party_name

    if qutation_doc.quotation_to == "Lead" :
        party_type = "Customer"
        party = frappe.db.get_value("Customer" , {"lead_name":qutation_doc.party_name},'name')
        
        if not party :
            from dynamic.terra.doctype.quotation.quotation import make_customer
            customer = make_customer(source_name,ignore_permissions=True)
            if customer :
                party = customer.name



    from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
    # from erpnext.accounts.party import get_party_account
    pe = frappe.new_doc("Payment Entry")
    pe.payment_type = "Receive"
    pe.mode_of_payment = "Cash"
    pe.company = qutation_doc.company
    pe.paid_to = (get_bank_cash_account(pe.mode_of_payment,pe.company) or {}).get("account")
    if pe.paid_to :
        pe.paid_to_account_currency = get_account_currency(pe.paid_to)
    pe.party_type = party_type
    pe.party = party
    pe.party_name = qutation_doc.customer_name

    pe.paid_amount = (qutation_doc.base_rounded_total or qutation_doc.base_grand_total) - (getattr(qutation_doc,'advance_paid',0))
    pe.received_amount = pe.paid_amount
    pe.received_amount_after_tax = pe.paid_amount
    # cash_detail = get_all_apyment_for_quotation(source_name)
    #modify to outstand amount
    row = pe.append('references',{})
    row.reference_doctype = "Quotation"
    row.reference_name = source_name
    
    row.outstanding_amount = pe.paid_amount
    row.allocated_amount = pe.paid_amount
    # if cash_detail!= False :
        # pe.paid_amount = cash_detail.get("outstand")
        # row.outstanding_amount = cash_detail.get("outstand") #modify to outstand amount
    cst_account = get_party_details(company=qutation_doc.company,date=None,
    party_type=party_type, 
    party=party,
    cost_center=None)
    pe.part_balance = cst_account.get('party_balance')
    pe.paid_from = cst_account.get('party_account')
    # pe.paid_from = get_party_account(pe.party_type,pe.party , pe.company)#cst_account.get('party_account')
    pe.paid_from_account_currency = cst_account.get('party_account_currency')
    pe.paid_from_account_balance = cst_account.get('account_balance')
    return pe



def get_all_apyment_for_quotation(qutation_name):
    sql=f'''
            select tper.parent,tper.reference_name ,tper.total_amount, 
            IFNULL(SUM(tper.allocated_amount),0) total_paid,
            (tper.total_amount-IFNULL(SUM(tper.allocated_amount),0))outstand
            from `tabPayment Entry Reference` tper
            where tper.reference_name='{qutation_name}' 
            GROUP by tper.reference_name
    '''
    data = frappe.db.sql(sql,as_dict=1)
    if len(data) > 0 :

        return data[0]
    else :
        return False


@frappe.whitelist()
def add_paid_amount(payment,*args,**Kwargs):
    if 'Terra' in Domains:
        if(payment.references[0].get('reference_doctype')=='Quotation'):
            outstand_amount = frappe.db.get_value('Quotation', payment.references[0].get('reference_name'),'outstand_amount') or 0
            frappe.db.set_value('Quotation', payment.references[0].get('reference_name'),'outstand_amount',outstand_amount + payment.total_allocated_amount )
        

@frappe.whitelist()
def cancel_amount_quotation(payment,*args,**Kwargs):
    if 'Terra' in Domains:
        if(payment.references[0].get('reference_doctype')=='Quotation'):
            outstand_amount = frappe.db.get_value('Quotation', payment.references[0].get('reference_name'),'outstand_amount') or 0
            frappe.db.set_value('Quotation', payment.references[0].get('reference_name'),'outstand_amount',outstand_amount - payment.total_allocated_amount )
        #     frappe.errprint(f'outstand_amount-->{outstand_amount}')
        #     frappe.errprint(f'payment.total_allocated_amount-->{payment.total_allocated_amount}')
        # ...

@frappe.whitelist()
def submit_supplier_quotation(doc ,*args ,**kwargs) :
      if 'Terra' in Domains:
      
        from dynamic.terra.doctype.supplier_quotation.supplier_quotation import submit_supplier_quotation as tera_submit_quotation
        tera_submit_quotation(doc) 





@frappe.whitelist()
def create_action_doc(source_name ,target_doc=None ):
    doctype = frappe.flags.args.doctype
    # source_doc = frappe.get_doc(doctype,docname)
    target_doc = frappe.new_doc("Actions")
    target_doc.customer_type = doctype
    target_doc.customer = source_name
    return target_doc

@frappe.whitelist()
def get_item_group_brand(doctype, txt, searchfield, start, page_len, filters):
    condition = ' 1=1 '
    item_group = filters.get("item_group") or ""
    brand = filters.get("brand") or ""
    if item_group:
        condition += f'AND item.item_group="{item_group}" '
    if brand:
        condition += f'AND item.brand="{brand}" '

    search_txt = "%%%s%%" % txt
    data = frappe.db.sql(
        f"""SELECT item.name,item.item_code,item.item_group,item.brand
        FROM `tabItem` item
			where {condition}
			and (item.name like '{search_txt}' )"""
    )
    return data

@frappe.whitelist()
def create_cst_appointment(source_name ,target_doc=None):
    source_doc = frappe.get_doc("Customer",source_name)
    target_doc = frappe.new_doc("Appointment")
    target_doc.customer_name = source_doc.customer_name
    target_doc.scheduled_time = now()
    return target_doc