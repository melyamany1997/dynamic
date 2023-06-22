# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _, scrub
from frappe.utils import add_days, add_to_date, flt, getdate
from six import iteritems

from erpnext.accounts.utils import get_fiscal_year


def execute(filters=None):
	return Analytics(filters).run()


class Analytics(object):
	def __init__(self, filters=None):
		self.filters = frappe._dict(filters or {})
		self.date_field = "transaction_date"

		
		self.get_period_date_ranges()

	def run(self):
		self.get_columns()
		self.get_data()
		# self.get_chart_data()
		self.get_chart_data(self.filters,self.columns,self.data)

		# Skipping total row for tree-view reports
		skip_total_row = 0

		return self.columns, self.data, None, self.chart, None, skip_total_row

	def get_columns(self):
		self.columns = [
			{"label": _('Week'), "fieldname": ('week'), "fieldtype": "Data", "width": 120}
		]
		self._status = [
				"Draft",
				"Open",
				"Replied",
				"Ordered",
				"Lost",
				"Cancelled",
				"Expired",
				"Rejected",
			]
		for status in self._status:
			self.columns.append(
				{"label": _(status), "fieldname": (status), "fieldtype": "Float", "width": 120,"default":0}
			)
		self.columns.append(
			{"label": _("Total"), "fieldname": "total", "fieldtype": "Float", "width": 100,"default":0}
		)

	def get_data(self):
		
		self.get_data_quotation()
		self.get_rows()

	def get_data_quotation(self):
		condition = "WHERE 1=1  "
		if self.filters.get("orderd") == "Yes":
			condition += "AND status = '%s' "%("Ordered")
		if self.filters.get("from_date") and self.filters.get("to_date"):
			if(self.filters.get("from_date") > self.filters.get("to_date")):
				frappe.throw(_("From Date must be before To Date"))
			condition += "AND {date_field} between '{from_date}' and '{to_date}' ".format(date_field=self.date_field,from_date = self.filters.from_date, to_date = self.filters.to_date)
		if self.filters.get("quotation"):
			condition += " AND name = '%s' "%(self.filters.get("sales_order"))

		sql = """SELECT name as entity,{date_field}, 1 as value_field ,status FROM `tabSales Order`
			{condition}
		""".format(condition=condition,date_field=self.date_field)
		self.entries = frappe.db.sql(sql,as_dict=1)
		self.entity_names = {}
		for d in self.entries:
			self.entity_names.setdefault(d.name, d.quotation_to)

	def get_rows(self):
		self.data = []
		self.get_periodic_data()

		self.labels_chart = []
		
		for entity, period_data in iteritems(self.entity_periodic_data):

			row = {
				"entity": entity,
			}
			
			for week, week_data in iteritems(period_data):
				row_test = {}
				row_test['week'] = week
				self.labels_chart.append(row_test['week']) 
				for status, status_qty in iteritems(week_data['status']):
					row_test[status] = status_qty["qty"]
					row_test['total'] = row_test.get('total',0) + status_qty["qty"]
				self.data.append(row_test)
		


	def get_periodic_data(self):
		self.entity_periodic_data = frappe._dict()
		
		for d in self.entries:
			#! change row data here
			year = (d.get(self.date_field)).isocalendar()[0]
			period = self.get_period(d.get(self.date_field)) #? get week name

				#? {2023: {'Week 5 2023': {'status': {'Open': {'qty': 2.0}}}, 'Week 6 2023': {'status': {'Open': {'qty': 1.0}}}}} 
			#!add status to key
			
			self.entity_periodic_data.setdefault(year, frappe._dict()).setdefault(period, frappe._dict()).setdefault('status', frappe._dict()).setdefault(d.status,frappe._dict()).setdefault('qty', 0.0)
			self.entity_periodic_data.setdefault(year, frappe._dict()).setdefault(period, frappe._dict()).setdefault('status', frappe._dict()).setdefault(d.status,frappe._dict()).setdefault('key', d.status)
	
			self.entity_periodic_data[year][period]['status'][d.status]['qty'] += flt(d.value_field)


	def get_period(self, posting_date):
		# period = "Week " + str(posting_date.isocalendar()[1]) + " " + str(posting_date.year)
		if self.filters.range == "Weekly":
			period = "Week " + str(posting_date.isocalendar()[1]) + " " + str(posting_date.year)
		elif self.filters.range == "Monthly":
			period = str(self.months[posting_date.month - 1]) + " " + str(posting_date.year)
		elif self.filters.range == "Quarterly":
			period = "Quarter " + str(((posting_date.month - 1) // 3) + 1) + " " + str(posting_date.year)
		else:
			year = get_fiscal_year(posting_date, company=self.filters.company)
			period = str(year[0])
		return period

	def get_period_date_ranges(self):
		from dateutil.relativedelta import MO, relativedelta

		from_date, to_date = getdate(self.filters.from_date), getdate(self.filters.to_date)

		increment = {"Monthly": 1, "Quarterly": 3, "Half-Yearly": 6, "Yearly": 12}.get(
			self.filters.range, 1
		)

		if self.filters.range in ["Monthly", "Quarterly"]:
			from_date = from_date.replace(day=1)
		elif self.filters.range == "Yearly":
			from_date = get_fiscal_year(from_date)[1]
		else:
			from_date = from_date + relativedelta(from_date, weekday=MO(-1))

		self.periodic_daterange = []
		for dummy in range(1, 53):
			if self.filters.range == "Weekly":
				period_end_date = add_days(from_date, 6)
			else:
				period_end_date = add_to_date(from_date, months=increment, days=-1)

			if period_end_date > to_date:
				period_end_date = to_date

			self.periodic_daterange.append(period_end_date)

			from_date = add_days(period_end_date, 1)
			if period_end_date == to_date:
				break


	def get_chart_data(self,filters, columns, data,income="", expense="", net_profit_loss=""):
	
		dict_status = {}
		datasets = []
		for status in self._status:
			dict_status[status] = []
			for row in self.data:
				row[status] = row.get(status,0)
				dict_status.get(status).append(row.get(status))
			datasets.append({"name": _(status), "values": dict_status.get(status)})

		chart = {
			'data':{
				'labels':self.labels_chart,
				'datasets':datasets
			},
			'type':'bar'
		}
		chart["type"] = "bar"

		chart["fieldtype"] = "Currency"
		self.chart = chart
