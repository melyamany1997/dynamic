# Copyright (c) 2023, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils.data import get_link_to_form


class CustomerRequest(Document):

    def on_submit(self):
        self.create_customer()

    def create_customer(self):
        default_customer_group = frappe.db.get_single_value(
            "Selling Settings", "default_distributer_customer_group")
        default_customer_territory = frappe.db.get_single_value(
            "Selling Settings", "default_distributer_territory")

        if not (default_customer_group and default_customer_territory):
            frappe.throw(
                _("Please set Distributer Settings in Selling Settings"))

        customer = frappe.new_doc("Customer")
        customer.customer_name = self.customer_name
        customer.customer_type = "Distributor"
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
            "link_title": self.customer_name,
        })

        address.insert()
		# link address to customer
        customer.customer_primary_address = address.name
        customer.save()

        lnk = get_link_to_form(customer.doctype, customer.name)
        frappe.msgprint(_("{} {} was Created").format(customer.doctype, lnk))
        self.status = "Approved"
        self.db_set("status", self.status)
