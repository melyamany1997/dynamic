// Copyright (c) 2022, Dynamic and contributors
// For license information, please see license.txt

frappe.ui.form.on("Installation Order", {
  // refresh: function(frm) {

  // }
  refresh: function (frm) {
    if (frm.doc.docstatus == 1 && frm.doc.pending_cars > 0) {
      frm.add_custom_button(
        __("Installation"),
        function () {
          frm.events.make_installation(frm);
        },
        __("Create")
      );
    }
  },
  setup: function (frm) {
    frm.custom_make_buttons = { "Car Installation": "Installation" };
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
    frm.set_query("installation_request", function () {
      return {
        filters: [
          ["docstatus", "=", 1],
          ["not_ordered_cars", ">", 0],
        ],
      };
    });
  },
  customer: function (frm) {
    frm.set_value("delegate", "");
    frm.set_value("delegate_name", "");
    frm.set_value("delegate_phone_number", "");
  },
  make_installation(frm) {
    frappe.model.open_mapped_doc({
      method:
        "dynamic.hardware_installations.doctype.installation_order.installation_order.make_installation",
      frm: frm,
    });
  },
  team(frm) {
    if (frm.doc.team) {
      frappe.call({
        method: "get_team_parties",
        doc: frm.doc,
        callback: function () {
          frm.refresh_fields(["installation_team_detail", "team"]);
        },
      });
    }
  },
  set_totals(frm) {
    frappe.call({
      method: "set_totals",
      doc: frm.doc,
      callback: function () {
        frm.refresh_fields(["items", "total_cars"]);
      },
    });
  },
});
frappe.ui.form.on("Installation Order Item", {
  items_add: function (frm, cdt, cdn) {
    frm.events.set_totals(frm);
  },
  items_remove: function (frm, cdt, cdn) {
    frm.events.set_totals(frm);
  },
  cars: function (frm, cdt, cdn) {
    frm.events.set_totals(frm);
  },
});
