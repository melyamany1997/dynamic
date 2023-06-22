


import frappe

from erpnext.selling.doctype.customer.customer import Customer
DOMAINS = frappe.get_active_domains()


class CustomerController(Customer):
    def before_save(self):
        # super(CustomerController,self).before_save()
        if 'Teba' in DOMAINS:
            if self.territory:
                parent_territory = frappe.db.get_value("Territory",self.territory,'parent_territory')
                if parent_territory:
                    self.db_set('parent_territory',parent_territory)