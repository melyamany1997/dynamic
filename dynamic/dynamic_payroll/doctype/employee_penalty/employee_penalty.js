// Copyright (c) 2023, Dynamic and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Penalty', {
	setup: function (frm) {
		frm.custom_make_buttons = {
			"Additional Salary": "Additional Salary",
		};
	},
	onload: function (frm) {
		frm.events.set_frm_query(frm)
	},
	refresh: function (frm) {
		if (frm.doc.docstatus == 1 && frm.doc.additional_salary == null) {
			frm.add_custom_button("Additional Salary", () => {
				frm.events.create_addtional_salary(frm)
			},
				__("Create"))
		}

	},
	set_frm_query(frm) {
		frm.set_query('salary_component', function () {
			return {
				filters: [
					["type", "=", "Deduction"],
				],
			};
		})
	},
	create_addtional_salary(frm) {
		frappe.call({
			method:
				"dynamic.dynamic_payroll.doctype.employee_penalty.employee_penalty.create_addtional_salary",
			args: {
				source_name: frm.doc.name
			}, //this.frm
			callback: function (r) {
				frm.refresh()
			}
		})
	}
});
