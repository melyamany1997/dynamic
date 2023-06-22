# Copyright (c) 2023, Dynamic and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns, data = [], []
    return InvestmentEquation(filters).run()


class InvestmentEquation(object):
	def __init__(self, filters=None):
		self.filters = frappe._dict(filters or {})
		self.from_date = self.filters.get('from_date')
		self.to_date = self.filters.get('to_date')
		self.company = self.filters.get('company')
		self.project = self.filters.get('project')
		self.cost_center = self.filters.get('cost_center')
		self.assets_filter = self.filters.get('asset_accounts') or []
		self.equity_filter = self.filters.get('equity_accounts') or []
		self.conditions = self.get_conditions()
		self.assets_accounts = self.get_accounts('assets', self.assets_filter) or []
		self.equity_accounts = self.get_accounts('equity', self.equity_filter) or []
		self.columns = self.get_columns()
		self.data = self.get_data()

	def get_accounts(self, field, accounts_filter=[]):
		conditions = ""
		if accounts_filter:
			filter_str = ",".join([f"'{x}'" for x in accounts_filter])
			conditions = f" and account in ({filter_str}) "

		sql = f"""
			select account from `tabinvestment Equation Account`
			where 
					parent = '{self.company}' 
					and parentfield = '{field}'

			{conditions}
		"""
		return frappe.db.sql_list(sql) or []

	def run(self):
		# self.get_columns()
		# self.get_data()
		return self.columns, self.data

	def get_columns(self):
		self.columns = [
			{
				"fieldname": "asset_account",
				"fieldtype": "Link",
				"label": _("Asset Account"),
				"options": "Account",
				"width": 150
			},
			{
				"fieldname": "asset_balance",
				"fieldtype": "Currency",
				"label": _("Value"),
				"width": 120
			},
			{
				"fieldname": "",
				"fieldtype": "Data",
				"label": _(""),
				"width": 120
			},
			{
				"fieldname": "equity_account",
				"fieldtype": "Link",
				"label": _("Equity Account"),
				"options": "Account",
				"width": 150
			},
			{
				"fieldname": "equity_balance",
				"fieldtype": "Currency",
				"label": _("Value"),
				"width": 120
			}
		]

		return self.columns

	def get_accounts_balances(self, field, accounts=[]):
		if not accounts:
			return []
		accounts_str = ",".join([f"'{x}'" for x in accounts])

		sql = f"""
		select
			account.name as {field}_account,
			IFNULL(SUM(CASE WHEN gl_entry.credit > 0 THEN -1 * gl_entry.credit WHEN gl_entry.debit > 0 THEN debit ELSE 0 END ) ,0) as {field}_balance
		from
			tabAccount account
		left join `tabGL Entry` gl_entry on
			gl_entry.account = account.name
			and gl_entry.docstatus = 1
			and gl_entry.is_cancelled <> 1
			and date(gl_entry.posting_date) BETWEEN date('{self.from_date}') AND date('{self.to_date}')
			{self.conditions}
		where
			account.company = '{self.company}'
			and  account.name in ({accounts_str})
		GROUP BY account.name
		ORDER BY account.name asc
		"""
		# if field == "equity" :
		# 	frappe.throw(sql)
		balances = frappe.db.sql(sql, as_dict=1) or []
		total_balance = sum([ x.get(f'{field}_balance') for x in balances])

		# frappe.msgprint(str(total_balance))
		# total_row = frappe._dict({
		# 	f"{field}_account" : _("Total"),
		# 	f"{field}_balance" : total_balance
		# })
		# balances.append({})
		# balances.append(total_row)
		# balances.append({})
		return balances, total_balance

	def get_data(self):
		self.data = []
		asset_data, asset_total = self.get_accounts_balances("asset", self.assets_accounts)
		equity_data, equity_total = self.get_accounts_balances("equity", self.equity_accounts)
		# frappe.msgprint(str(asset_total))
		# frappe.msgprint(str(equity_total))
		diff_row = {
			"asset_account" : f"""<b>{_("Difference")}</b>""" ,
			"asset_balance" : abs((asset_total or 0) - (equity_total or 0)),
		}
		total_row = frappe._dict({
			f"asset_account" : f"""<b>{_("Asset")} {_("Total")}</b>""",
			f"asset_balance" : asset_total ,
			f"equity_account" : f"""<b>{_("Equity")} {_("Total")}</b>""",
			f"equity_balance" : equity_total,
		})
		l1 = len(asset_data)
		l2 = len(equity_data)
		max_len = max(l1,l2)

		for i in range(0,max_len) :
			row = frappe._dict()
			if i < l1 :
				row.update(asset_data[i])

			if i < l2 :
				row.update(equity_data[i])

			self.data.append(row)


		# self.data.append({})
		self.data.append(total_row)
		# self.data.append({})
		self.data.append(diff_row)
		# self.data.append({})
		return self.data

	def get_conditions(self):
		conditions = ""

		filters = self.filters

		data = filters.get("company")
		if data:
			conditions += f" and gl_entry.company = '{data}' "

		data = filters.get("project")
		if data:
			conditions += f" and gl_entry.project = '{data}' "

		data = filters.get("cost_center")
		if data:
			conditions += f" and gl_entry.cost_center = '{data}' "

		return conditions
