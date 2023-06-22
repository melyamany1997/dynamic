# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class AttendanceRule(Document):
	def validate(self):

		list = []
		if self.fingerprint_forgetten_penlaity_salary_component:
			list.append(str(self.fingerprint_forgetten_penlaity_salary_component))
		if self.salary_componat_for_late:
			list.append(str(self.salary_componat_for_late))
		if self.salary_component_for_late_penalty:
			list.append(str(self.salary_component_for_late_penalty))
		if self.absent__component:
			list.append(str(self.absent__component))
		if self.abset_penalty_component:
			list.append(str(self.abset_penalty_component))
		if self.overtime_salary_component:
			list.append(str(self.overtime_salary_component))
		message = '<ol>'
		count = 0
		if len(list) > 0:
			if list.count(str(self.fingerprint_forgetten_penlaity_salary_component)) > 1 :
				message += '<li>' + _('Fingerprint Forgetten penlaity Salary Component') + '</li>'
				count +=1
			if list.count(str(self.salary_componat_for_late)) > 1 :
				message += '<li>' + _('Salary Componat for Late')+ '</li>'
				count +=1
			if list.count(str(self.salary_component_for_late_penalty)) > 1 :
				message += '<li>' + _('Salary Component For Late Penalty')+ '</li>'
				count +=1
			if list.count(str(self.absent__component)) > 1 :
				message += '<li>' + _('Absent  Component')+ '</li>'
				count +=1
			if list.count(str(self.abset_penalty_component)) > 1 :
				message += '<li>' + _('Absent Penalty Component')+ '</li>'
				count +=1

			if list.count(str(self.overtime_salary_component)) > 1 :
				message += '<li>' + _('Overtime Salary Component') + '</li>'
				count +=1

			message += '</ol>'
			if count :
				frappe.throw (_(" *   this elements is Duplicated <br> {}".format(message)))

		self.set_col_values()
		self.set_fingerpenality_levels()
		self.set_lesstimepenality_levels()


	def set_col_values(self):
		for i in self.late_role_table :
			level_dict= []
			level_dict.append(float(i.level_onefactor) or 0)
			level_dict.append(float(i.level_towfactor) or 0)
			level_dict.append(float(i.level__threefactor) or 0)
			level_dict.append(float(i.level_fourfactor) or 0)
			level_dict.append(float(i.leve_five_factor )or 0 )
			
			for e in level_dict :
				try:
					level_dict.remove(0)
				except:
					pass
			for f in range(0 , 6):
				if f > len(level_dict) :
					level_dict.append(max(level_dict)) 
				
			level_dict.sort()
			i.level_onefactor = level_dict[0]
			i.level_towfactor =level_dict[1] 
			i.level_threefactor = level_dict[2]
			i.level_fourfactor = level_dict[3]
			i.level_five_factor = level_dict[4]
	def set_fingerpenality_levels(self):
		if len( getattr(self,'fingerprint_factors',[]))>0 :
			# max_factor = max([i.factor for i in  getattr(self,'fingerprint_factors',[])])
			for i in getattr(self,'fingerprint_factors',[]):
				i.level = i.idx
				i.factor = i.factor #or max_factor
	def set_lesstimepenality_levels(self):
		if len( getattr(self,'less_penalty_factor_rules',[]))>0 :
			# max_factor = max([i.factor for i in  getattr(self,'less_penalty_factor_rules',[])])
			for i in getattr(self,'less_penalty_factor_rules',[]):
				i.level = i.idx
				i.factor = i.factor #or max_factor






