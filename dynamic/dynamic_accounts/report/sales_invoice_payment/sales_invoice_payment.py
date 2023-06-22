# Copyright (c) 2023, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns, data = [], []
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters):
    columns = [
        {
            "label": _("Invoice"),
            "fieldname": "invoice_name",
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "width": 250
        },
        {
            "label": _("Customer"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 200
        },
        {
            "label": _("Invoice Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": _("Total Amount"),
            "fieldname": "total_amount",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "label": _("Paid"),
            "fieldname": "paid_amount",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "label": _("Outstanding"),
            "fieldname": "outstanding_amount",
            "fieldtype": "Float",
            "width": 120
        },
    ]
    return columns


def get_data(filters):
	data = []

	conditions = get_conditions(filters)

	sql = f"""
		select
			* ,
			(t.total_amount-t.paid_amount) as outstanding_amount
		from
		(
		select
			invoice.name as invoice_name ,
			invoice.customer,
			invoice.posting_date ,
			(case
				when invoice.disable_rounded_total = 1 then invoice.base_grand_total
				else invoice.base_rounded_total
			end) as total_amount ,
			SUM(IFNULL((case when credit > 0 then credit else debit end),0)) as paid_amount
		from
			`tabSales Invoice` invoice
		left join  
		`tabGL Entry` gl_entry on
			invoice.name = gl_entry.against_voucher
			and gl_entry.against_voucher_type = 'Sales Invoice'
			and gl_entry.docstatus = 1
			and gl_entry.is_cancelled <> 1
			and gl_entry.voucher_type in ('Payment Entry' , 'Journal Entry')
		where
			invoice.docstatus = 1
			{conditions}
		GROUP BY
			invoice.name
		ORDER BY
			date(invoice.posting_date) asc ,
			invoice.posting_time asc
		) t

	"""
	# frappe.throw(str(sql))
	data = frappe.db.sql(sql, as_dict=1)
	return data


def get_conditions(filters):
    conditions = " "
    if filters.get('from_date') and filters.get('to_date'):
        conditions += f" and date(invoice.posting_date) BETWEEN date('{filters.get('from_date')}') AND date('{filters.get('to_date')}')"
    else:
        data = filters.get('from_date')
        if data:
            conditions += f" and date(invoice.posting_date) >= date('{data}')"

        data = filters.get('to_date')
        if data:
            conditions += f" and date(invoice.posting_date) <= date('{data}')"

    data = filters.get('customer')
    if data:
        conditions += f" and invoice.customer = '{data}' "

    data = filters.get('invoice')
    if data:
        conditions += f" and invoice.name = '{data}' "

    return conditions
