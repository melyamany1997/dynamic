# Copyright (c) 2022, Dynamic and contributors
# For license information, please see license.txt

import frappe

from frappe import _


def execute(filters=None):
    return employee_schedule(filters).run()


class employee_schedule(object):
    def __init__(self, filters=None):
        self.filters = frappe._dict(filters or {})

    def run(self):
        self.get_columns()
        self.get_data()
        return self.columns, self.data

    def get_columns(self):
        # add columns wich appear data
        self.columns = [
            {
                "fieldname": "from_time",
                "fieldtype": "Date",
                "label": _("From"),
                "width": 150
            },
            {
                "fieldname": "to_time",
                "fieldtype": "Date",
                "label": _("To"),
                "width": 150
            },
            {
                "fieldname": "employee",
                "fieldtype": "Link",
                "label": _("Employee"),
                "width": 120,
                "options": "Employee",


            },
            {
                "fieldname": "installation_order",
                "fieldtype": "Link",
                "label": _("Installation Order"),
                "width": 120,
                "options": "Installation Order",
            },
            {
                "fieldname": "installation_request",
                "fieldtype": "Link",
                "label": _("Installation Request"),
                "width": 120,
                "options": "Installation Request",
            },
            {
                "fieldname": "team",
                "fieldtype": "Link",
                "label": _("Installation Team"),
                "width": 120,
                "options": "Installation Team",
            },
        ]
        return self.columns

    def get_data(self):
        self.data = []
        self.conditions, self.values = self.get_conditions(self.filters)

        data_query = f"""
			select * 
			from `tabEmployee Schedule` p
			where {self.conditions}
			
		"""

        self.data = frappe.db.sql(data_query, values=self.values, as_dict=1)

        return self.data

    def get_conditions(self, filters):
        conditions = "1=1 "
        values = dict()

        if filters.get("from_time"):
            if filters.get("from_time") and filters.get("to_time"):
                conditions += " AND date(p.from_time)  >= date(%(from_time)s)  AND date(p.to_time)  <= date(%(to_time)s)"
                values["from_time"] = filters.get("from_time")
                values["to_time"] = filters.get("to_time")

            if filters.get("from_time") and not filters.get("to_time"):
                conditions += " AND date(p.from_time)  = date(%(from_time)s) "
                values["from_time"] = filters.get("from_time")

        if filters.get('installation_order'):
            conditions += " AND p.installation_order  =  %(installation_order)s "
            values["installation_order"] = filters.get("installation_order")

        if filters.get('installation_request'):
            conditions += " AND p.installation_request  =  %(installation_request)s "
            values["installation_request"] = filters.get(
                "installation_request")

        if filters.get('team'):
            conditions += " AND p.team  =  %(team)s "
            values["team"] = filters.get("team")

        if filters.get('employee'):
            conditions += " AND p.employee  =  %(employee)s "
            values["employee"] = filters.get("employee")
        return conditions, values
