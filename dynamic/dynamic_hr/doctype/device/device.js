// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Device", {
  refresh: function (frm) {
    frappe.realtime.on("update_progress_attendance_calculation", (data) => {
      frappe.show_progress(
        __("Calculating Attendance"),
        data.progress,
        data.total
        // data.footer
      );
    });
    frappe.realtime.on("update_progress_device", (data) => {
      frappe.show_progress(
        __("Getting Logs"),
        data.progress,
        data.total
        // __("Getting Logs")
      );
    });

    if (!frm.is_new()) {
      if (frm.doc.is_active) {
        frm.add_custom_button(
          __("Get Attendance"),
          function () {
            frappe.call({
              doc: frm.doc,
              method: "get_attendance",
              freeze: true,
              callback: function (r) {
                // frappe.hide_progress();
                // frappe.msgprint(__("Done"));
                frm.refresh();
              },
            });
          },
          __("Actions")
        );
        // frm.add_custom_button(
        //   __("Map Employees"),
        //   function () {
        //     frappe.call({
        //       method: "dynamic.dynamic_hr.doctype.device.device.map_employees",
        //       freeze: true,
        //       callback: function (r) {
        //         frappe.msgprint(__("Done"));
        //         frappe.hide_progress();
        //         frm.refresh();
        //       },
        //     });
        //   },
        //   __("Actions")
        // );
        frm.add_custom_button(
          __("Create Employee Checkin"),
          function () {
            frappe.call({
              method:
                "dynamic.dynamic_hr.doctype.device.device.create_employee_checkin",
              freeze: true,
              callback: function (r) {
                // frappe.msgprint(__("Done"));
                frappe.hide_progress();
                frm.refresh();
              },
            });
          },
          __("Actions")
        );
        frm.add_custom_button(
          __("Calculate Attendance"),
          function () {
            frappe.call({
              method:
                "dynamic.dynamic_hr.doctype.device.device.calculate_attendance",
              freeze: true,
              callback: function (r) {
                // frappe.msgprint(__("Done"));
                frappe.hide_progress();
                frm.refresh();
              },
            });
          },
          __("Actions")
        );
      }
    }
  },
});
