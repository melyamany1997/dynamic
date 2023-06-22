// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Calculation', {
	setup:function (frm){
		frm.set_query('payroll_period', function(doc) {
			return {
				filters: {
					"is_closed": 0,
					"docstatus":0
				}
			};
		});
	},
	payroll_period:function(frm) {
		if (frm.doc.payroll_period){
			frappe.call({

					method:"frappe.client.get" ,
					args:{
   						doctype: "Payroll Period",
   						name : frm.doc.payroll_period


   				   			},callback:function(r){

   				   				if (r.message)
								{
									if ( r.message.is_closed  )
										frm.doc.payroll_period = null
								}
   				   				frm.refresh_field("payroll_period")

   				   			}
				})
		}
	},
	refresh: function(frm) {

			frappe.call({

					method:"frappe.client.get" ,
					args:{
   						doctype: "Payroll Period",
   						name : frm.doc.payroll_period


   				   			},callback:function(r){
   				   				if (r.message)
								{
									if ( r.message.is_closed  )
											return false
									else
										var payroll_valid = true
				if (!frm.is_new()) {
		 		// tools
				frm.add_custom_button(__('Sheet Details'), function() {
				frappe.route_options = {

					"from_date": frm.doc.from_date,
					"to_date": frm.doc.to_date,
					"company": frm.doc.company

				};
				frappe.set_route("query-report", "Attendance Sheet Details");
			}, __('View'));

		 		if (!payroll_valid)
				{
					frappe.msgprint(__("Period Is Closed"));
					return
				}


			 	if (frm.doc.docstatus == 1){
			 		frm.add_custom_button(__("Recalculate"),
									function() {
										frm.events.Calculate_attendance(frm);

									}).addClass("btn-primary");

					frm.add_custom_button(__("Post Additional Salaries"),
										function() {
										frm.events.Post_attendance(frm);

									}).addClass("btn-primary");

			 	}else {
			 		frm.add_custom_button(__("Calculate"),
									function() {
										frm.events.Calculate_attendance(frm);

									}).addClass("btn-primary");
				}
		 	}

								}


   				   			}
				})




			frappe.realtime.on('update_progress_attendance_calculation', (data) => {

				    frappe.show_progress(__('Calculating Attendance'),  data.progress , data.total,data.footer)
			});


	},

	Calculate_attendance: function (frm) {




			var d = new frappe.ui.Dialog({
				title: __("Calculate to Employees"),
				fields: [
					{fieldname: "sec_break", fieldtype: "Section Break", label: __("Filter Employees By (Optional)")},
					// {fieldname: "company", fieldtype: "Link", options: "Company", label: __("Company"), default: frm.doc.company, read_only:1},
					// {fieldname: "currency", fieldtype: "Link", options: "Currency", label: __("Currency"), default: frm.doc.currency, read_only:1},
					{fieldname: "grade", fieldtype: "Link", options: "Employee Grade", label: __("Employee Grade")},
					{fieldname:'department', fieldtype:'Link', options: 'Department', label: __('Department')},
					{fieldname:'designation', fieldtype:'Link', options: 'Designation', label: __('Designation')},
					{fieldname:"employee", fieldtype: "Link", options: "Employee", label: __("Employee")}
				],
				primary_action: function() {
					var data = d.get_values();
					frappe.call({
						doc: frm.doc,
						method: "Calculate_attendance",
						args: data,
						freeze: true,
						callback: function(r) {

								d.hide();

						}
					});
				},
				primary_action_label: __('Calculate')
			});


			d.show();
	},
	Post_attendance: function (frm) {
		var d = new frappe.ui.Dialog({
				title: __("Post for Employees"),
				fields: [
					{fieldname: "sec_break", fieldtype: "Section Break", label: __("Filter Employees By (Optional)")},
					// {fieldname: "company", fieldtype: "Link", options: "Company", label: __("Company"), default: frm.doc.company, read_only:1},
					// {fieldname: "currency", fieldtype: "Link", options: "Currency", label: __("Currency"), default: frm.doc.currency, read_only:1},
					{fieldname: "grade", fieldtype: "Link", options: "Employee Grade", label: __("Employee Grade")},
					{fieldname:'department', fieldtype:'Link', options: 'Department', label: __('Department')},
					{fieldname:'designation', fieldtype:'Link', options: 'Designation', label: __('Designation')},
					{fieldname:"employee", fieldtype: "Link", options: "Employee", label: __("Employee")}
				],
				primary_action: function() {
					var data = d.get_values();
					frappe.call({
						doc: frm.doc,
						method: "on_submit",
						args: data,
						freeze: true,
						callback: function(r) {

								d.hide();

						}
					});
				},
				primary_action_label: __('Post')
			});


			d.show();

								// frappe.call({
								// 			doc: frm.doc,
								// 			method: "on_submit",
								//
								// 			callback: function(r) {
								// 				frappe.msgprint(__("Done"));
								// 				// frappe.hide_progress();
								//
								// 			},
								// 			freeze: true
								// 		});
	},


});
