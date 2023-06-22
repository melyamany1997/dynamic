from dynamic.api import get_item_price
import frappe
from frappe.model.mapper import get_mapped_doc

from werkzeug.wrappers import Response

import json

from frappe.utils.data import nowdate
from frappe import _
from erpnext import get_company_currency, get_default_company, get_default_cost_center

def elevana_lead_before_insert(doc, fun=''):
    set_sales_person(doc)


def set_sales_person(doc):
    # frappe.msgprint('ss')
    if not doc.sales_person:
        employee = frappe.db.get_value(
            "Employee", {'user_id': frappe.session.user}, 'name')
        if employee:
            sales_person = emp = frappe.db.get_value(
                "Sales Person", {'employee': employee}, 'name')
            if sales_person:
                doc.sales_person = sales_person


@frappe.whitelist()
def make_quotation(source_name, target_doc=None):
    def set_missing_values(source, target):
        _set_missing_values(source, target)

    target_doc = get_mapped_doc(
        "Lead",
        source_name,
        {"Lead": {"doctype": "Quotation", "field_map": {"name": "party_name"}}},
        target_doc,
        set_missing_values,
    )
    target_doc.quotation_to = "Lead"
    target_doc.run_method("set_missing_values")
    target_doc.run_method("set_other_charges")
    target_doc.run_method("calculate_taxes_and_totals")

    return target_doc


def _set_missing_values(source, target):
    address = frappe.get_all(
        "Dynamic Link",
        {
            "link_doctype": source.doctype,
            "link_name": source.name,
            "parenttype": "Address",
        },
        ["parent"],
        limit=1,
    )

    contact = frappe.get_all(
        "Dynamic Link",
        {
            "link_doctype": source.doctype,
            "link_name": source.name,
            "parenttype": "Contact",
        },
        ["parent"],
        limit=1,
    )

    if address:
        target.customer_address = address[0].parent

    if contact:
        target.contact_person = contact[0].parent

    if getattr(source, 'sales_person', None):
        target.set('sales_team', [])
        target.append('sales_team', {
            "sales_person": getattr(source, 'sales_person', None),
            "allocated_percentage": "100",
            # "incentives":"150"
        })

        # dynamic.dynamic.elevana.api.get_customer_name


@frappe.whitelist(allow_guest=1)
def get_customer_name(*args, **kwargs):
    # get data
    data = False
    respone = Response()
    try:
        data = json.loads(frappe.request.data)
    except Exception as e:
        frappe.local.response['message'] = f"Error Accourd   {e}"
        frappe.local.response['http_status_code'] = 400

    if data:
        # check phone number
        phone_number = data.get("phone")
        user_extension = data.get("user_extension")
        if not phone_number:
            # frappe.local.response['message'] = "Customer name required"
            # frappe.local.response['http_status_code'] = 400
            respone.data = "error!"
            return

        if user_extension:
            user = frappe.db.get_value(
                "User", {"extension": user_extension}, 'name')
            if user:
                phone_call = frappe.new_doc("Phone Call")
                phone_call.posting_date = nowdate()
                phone_call.naming_series = 'PHN-CLL-.####'
                phone_call.user = user
                phone_call.phone_number = phone_number
                phone_call.save()
        sql = frappe.db.sql(f""" SELECT link_title FROM 
            `tabDynamic Link` WHERE parent in  (SELECT parent From `tabContact Phone` WHERE phone =  "{phone_number}" ) """, as_dict=1)

        if sql and len(sql) > 0:
            respone.data = str(sql[-1].get("link_title"))
        else:
            respone.data = str(phone_number)
        return respone


@frappe.whitelist()
def get_item_list(*args, **kwargs):
    price_list = frappe.db.get_single_value(
        "E Commerce Settings", "price_list")
    hub_items = frappe.get_list(
        "Item",
        filters={
            "publish_in_hub": 1,
            "disabled": 0
        },
        ignore_permissions=True,
        fields=[
            'item_code',
            'item_name',
            'item_group',
            'description',
            'item_code',
            'hub_warehouse as warehouse'
        ]
    )

    for item in hub_items:
        item.price = get_item_price(item.item_code, price_list) or 0
        item.stock_availability = "In Stock" if \
            frappe.db.get_value(
            "Bin",
            filters={
                        "item_code": item.item_code,
                        "warehouse": item.warehouse
                    },
            fieldname='actual_qty') or 0 \
            else "Out of Stock"

    frappe.response['items'] = hub_items





@frappe.whitelist()
def create_customer(*args, **kwargs):

    data = json.loads(frappe.request.data)
    # return data
    customer_name = data.get('customer_name')
    phone_no = data.get('phone_no')
    customer_group = frappe.db.get_single_value("E Commerce Settings", "default_customer_group")
    customer_territory = frappe.db.get_single_value("E Commerce Settings", "default_customer_territory")

    if not customer_name :
        frappe.response['status_code'] = 400
        frappe.response['message'] = _("{} is required").format(_('Customer Name'))
        return

    if not phone_no :
        frappe.response['status_code'] = 400
        frappe.response['message'] = _("{} is required").format(_('Phone No'))
        return

    if not customer_group :
        frappe.response['status_code'] = 400
        frappe.response['message'] = _("{} is required").format(_('Customer Group'))
        return

    if not customer_group :
        frappe.response['status_code'] = 400
        frappe.response['message'] = _("{} is required").format(_('Customer Territory'))
        return


    customer = frappe.new_doc('Customer')
    customer.customer_name = customer_name 
    customer.customer_group = customer_group
    customer.territory = customer_territory
    customer.phone_no = phone_no
    customer.save(ignore_permissions=True)
    frappe.response['customer'] = customer






@frappe.whitelist()
def create_sales_order(*args, **kwargs):
    # return json.loads(frappe.request.data)
    data = json.loads(frappe.request.data)

    customer_name = data.get('customer')
    items = data.get('items')
    customer = None
    # return frappe.get_doc("Customer" , customer_name)
    # return frappe.db.exists("Customer" , "pewter")
    if frappe.db.exists("Customer" , customer_name) :
        customer = frappe.get_doc("Customer" , customer_name)

    company = frappe.db.get_single_value("E Commerce Settings", "company")
    price_list = frappe.db.get_single_value("E Commerce Settings", "price_list")


    if not customer_name :
        frappe.response['status_code'] = 400
        frappe.response['message'] = _("{} is required").format(_('Customer'))
        return

    if not customer :
        frappe.response['status_code'] = 400
        frappe.response['message'] = _("{} is invalid").format(_('Customer'))
        return
    
    # print (frappe.request.post)
    print (type(items))
    if type(items) is str :
        items = json.loads(str(items))
    
    print (type(items))
    # return

    if not items :
        frappe.response['status_code'] = 400
        frappe.response['message'] = _("{} is required").format(_('Items'))
        return


    
     
    order = frappe.new_doc("Sales Order")
    order.customer = customer.name
    order.company = company
    order.currency = get_company_currency(company)
    order.price_list = price_list
    order.order_type = "Sales"
    order.delivery_date = nowdate()
    
    order.conversion_rate = 1
    order.cost_center = get_default_cost_center(company)


    for item in items or []:
        #it=frappe._dict(it)
        item_doc = None
        item_code = item.get("item_code")
        if frappe.db.exists("Item" , item_code) :
            item_doc = frappe.get_doc("Item" , item_code)

        if not item_doc :
            frappe.response['status_code'] = 400
            frappe.response['message'] = _("{} is invalid").format(_('Item'))
            return
        
        row = order.append("items",{})
        row.item_code = item_doc.item_code
        row.warehoue = item_doc.hub_warehouse
        row.qty= item.get ("qty")
        row.price_list_rate= item.get ("rate")
    
    order.save(ignore_permissions=True)
    frappe.response['order'] = order

















