// Copyright (c) 2022, Dynamic and contributors
// For license information, please see license.txt

frappe.ui.form.on("Installation Request", {
  refresh: function (frm) {
    if (frm.doc.docstatus == 1 && frm.doc.not_ordered_cars > 0) {
      frm.add_custom_button(
        __("Installation Order"),
        function () {
          frm.events.make_installation_order(frm);
        },
        __("Create")
      );
    }
  },
  setup: function (frm) {
    frm.custom_make_buttons= {"Installation Order":"Installation Order"};
    frm.set_query("delegate", function () {
      return {
        filters: [["customer", "=", frm.doc.customer]],
      };
    });
    frm.set_query("sales_order", function () {
      return {
        filters: [["docstatus", "=", 1]],
      };
    });
  },
  customer: function (frm) {
    frm.set_value("delegate", "");
    frm.set_value("delegate_name", "");
    frm.set_value("delegate_phone_number", "");
  },
  make_installation_order(frm) {
    frappe.model.open_mapped_doc({
      method:
        "dynamic.hardware_installations.doctype.installation_request.installation_request.make_installation_order",
      frm: frm,
    });
  },
});
