// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Device Log', {
	refresh: function (frm) {
	  },
	  log_time: function (frm) {
		if (frm.doc.log_time) {
		  let today = new Date(frm.doc.log_time);
		  frm.doc.log_date =
			today.getFullYear() +
			"-" +
			(today.getMonth() + 1) +
			"-" +
			today.getDate();
		  frm.doc.time_log =
			today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();
		} else {
		  frm.doc.log_date = "";
		  frm.doc.time_log = "";
		}
		frm.refresh_field("log_date");
		frm.refresh_field("time_log");
	  },
});
