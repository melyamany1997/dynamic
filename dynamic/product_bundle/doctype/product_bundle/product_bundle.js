frappe.ui.form.on("Product Bundle", {
  validate(frm) {
    frm.events.get_items_cost(frm);
  },
  refresh(frm) {
    // your code here
    frm.add_custom_button(
      __("Update Cost"),
      function () {
        frm.events.get_items_cost(frm);
      },
      __("Actions")
    );
  },
  get_items_cost: function (frm) {
    frm.doc.items.forEach((item) => {
      frm.events.get_item_cost(frm, item.doctype, item.name);
    });
  },

  set_total_cost: function (frm) {
    frm.doc.total_cost = 0;

    frm.doc.items.forEach((item) => {
      item.qty = item.qty || 0;
      item.cost = item.cost || 0;
      item.total_cost = item.cost * item.qty;
      frm.doc.total_cost += item.total_cost;
    });
    frm.refresh_field("total_cost");
    frm.refresh_field("items");
  },
  get_item_cost: function (frm, cdt, cdn) {
    var item = locals[cdt][cdn];
    if (item.item_code) {
      frappe.call({
        method:
          "dynamic.product_bundle.doctype.product_bundle.product_bundle.get_item_valuation_rate",
        args: {
          item_code: item.item_code,
          company: frappe.defaults.get_user_default("Company"),
          warehouse: "",
        },
        callback: function (r) {
          if (r.message) {
            item.cost = r.message.valuation_rate || 0;
            frm.events.set_total_cost(frm);
          }
        },
      });
    }
  },
});

frappe.ui.form.on("Product Bundle Item", {
  item_code: function (frm, cdt, cdn) {
    // your code here
    frm.events.get_item_cost(frm, cdt, cdn);
  },
  qty: function (frm, cdt, cdn) {
    frm.events.set_total_cost(frm);
  },
  items_add: function (frm, cdt, cdn) {
    frm.events.set_total_cost(frm);
  },
  items_remove: function (frm, cdt, cdn) {
    frm.events.set_total_cost(frm);
  },
});
