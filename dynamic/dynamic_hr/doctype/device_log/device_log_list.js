frappe.listview_settings["Device Log"] = {
  onload: function (list_view) {
    // list_view.page.add_inner_button(
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
    list_view.page.add_inner_button(
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
  },
};
