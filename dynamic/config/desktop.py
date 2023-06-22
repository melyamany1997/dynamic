# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"module_name": "dynamic",
			"color": "grey",
			"icon": "octicon octicon-file-directory",
			"type": "module",
			"label": _("Dynamic")
		},
		# {
		# "module_name": "ifi",
		# "color": "#8e44ad",
		# "icon": "fa fa-puzzle-piece",
		# # "icon": "octicon octicon-rocket",
		# "type": "module",
		# "label": _("IFI")
		# },
	]
