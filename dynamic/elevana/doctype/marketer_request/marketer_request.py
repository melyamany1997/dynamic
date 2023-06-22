# Copyright (c) 2023, Dynamic and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from frappe.utils.data import get_link_to_form
from frappe import _


class MarketerRequest(Document):
    def on_submit(self):
        self.create_customer()
        self.create_sales_partner()
        self.status = "Approved"
        self.db_set("status", self.status)

    def create_sales_partner(self):
        default_customer_territory = frappe.db.get_single_value(
            "Selling Settings", "default_marketer_territory")

        if not default_customer_territory:
            frappe.throw(
                _("Please set Marketer Settings in Selling Settings"))

        sales_partner = frappe.new_doc("Sales Partner")
        sales_partner.partner_name = self.marketer_name
        sales_partner.commission_rate = self.commission_rate
        sales_partner.partner_type = self.partner_type
        sales_partner.ref_doctype = self.doctype
        sales_partner.ref_docname = self.name
        sales_partner.territory = default_customer_territory
        sales_partner.set("item_groups", [])
        for row in self.item_groups:
            sales_partner.append('item_groups', {
                "item_group": row.item_group
            })
        sales_partner.insert()

        lnk = get_link_to_form(sales_partner.doctype, sales_partner.name)
        frappe.msgprint(_("{} {} was Created").format(
            sales_partner.doctype, lnk))

    def create_customer(self):
        default_customer_group = frappe.db.get_single_value(
            "Selling Settings", "default_marketer_customer_group")
        default_customer_territory = frappe.db.get_single_value(
            "Selling Settings", "default_marketer_territory")

        if not (default_customer_group and default_customer_territory):
            frappe.throw(
                _("Please set Marketer Settings in Selling Settings"))

        customer = frappe.new_doc("Customer")
        customer.customer_name = self.marketer_name
        customer.customer_type = "Marketer"
        customer.customer_group = default_customer_group
        customer.territory = default_customer_territory
        customer.ref_doctype = self.doctype
        customer.ref_docname = self.name
        customer.save()
        # create Address
        address_type = "Billing"

        address = frappe.new_doc("Address")
        address.address_type = address_type
        address.address_title = customer.name
        address.address_line1 = self.address_line
        address.city = self.city
        address.country = self.country

        address.set("links", [])
        address.append("links", {
            "link_doctype": customer.doctype,
            "link_name": customer.name,
            "link_title": customer.customer_name,
        })
        # add link ref to address
        address.append("links", {
            "link_doctype": self.doctype,
            "link_name": self.name,
            "link_title": self.marketer_name,
        })

        address.insert()
        # link address to customer
        customer.customer_primary_address = address.name
        customer.save()

        lnk = get_link_to_form(customer.doctype, customer.name)
        frappe.msgprint(_("{} {} was Created").format(customer.doctype, lnk))
