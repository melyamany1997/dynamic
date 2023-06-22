// Copyright (c) 2022, Dynamic and contributors
// For license information, please see license.txt

frappe.ui.form.on("Car Installation", {
  setup(frm) {
    let get_item_query = () => {
      return {
        query:
          "dynamic.hardware_installations.doctype.car_installation.car_installation.get_item_query",
        filters: {
          sales_order: frm.doc.sales_order,
        },
      };
    };
    frm.set_query("accessories", "installation_accessories", get_item_query);
    frm.set_query(
      "accessories_warehouse",
      "installation_accessories",
      function () {
        return { filters: [["is_group", "=", 0]] };
      }
    );
    frm.set_query("gps_warehouse", function () {
      return { filters: [["is_group", "=", 0]] };
    });
    frm.set_query("gps_item_code", get_item_query);
  },
  refresh: function (frm) {
    frm.set_query("installation_order", function () {
      return {
        filters: [["docstatus", "=", "1"]],
      };
    });

    frm.set_query("serial_number", function () {
      return {
        filters: [
          ["item_code", "=", frm.doc.gps_item_code],
          ["status", "=", "Active"],
        ],
      };
    });

    frm.set_query("gps_item_code_alt", function () {
      return {
        filters: [
          ["item_group", "=", "Queclink devices"],
        ],
      };
    });

    frm.set_query("gps_serial_number", function () {
      return {
        filters: [
          ["item_code", "=", frm.doc.gps_item_code],
          ["status", "=", "Active"],
        ],
      };
    });
  },
  car: function (frm) {
    if (frm.doc.car) {
      frappe.call({
        method: "get_car_data",
        doc: frm.doc,
        callback: function () {
          frm.refresh_fields();
        },
      });
    }
  },

  installation_order: function (frm) {
    if (frm.doc.installation_order) {
      frappe.call({
        method: "get_cst_delgate",
        doc: frm.doc,
        callback: function () {
          frm.refresh_fields();
        },
      });
    }
  },
  accessories: function (frm) {
    // if(frm.doc.accessories){
    // 	frappe.call({
    // 		method: 'frappe.client.get_value',
    // 		args: {
    // 		doctype: 'Item',
    // 		name: frm.doc.accessories,
    // 		fieldname: 'item_name'
    // 		},
    // 		   callback: function(r){
    // 			   frm.set_value('accessories_name',r.message.item_name)
    // 			//    frm.refresh_fields('accessories_name')
    // 			// frm.refresh()
    // 		}
    // 	});
    // }
  },
  gps_serial_number: function (frm) {
    if (frm.doc.serial_number) {
      frappe.call({
        method: "get_serial_gps",
        doc: frm.doc,
        callback: function () {
          frm.refresh_fields();
        },
      });
    }
  },
  team: function (frm) {
    if (frm.doc.team) {
      frappe.call({
        method: "get_team",
        doc: frm.doc,
        callback: function () {
          frm.refresh_fields();
        },
      });
    }
  },
});

frappe.ui.form.on(
  "Installation Accessories",
  "accessories_type",
  function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    console.log("chaged");
    if (row.accessories_type === "External") {
      let accessories_df = frappe.meta.get_docfield(
        "Installation Accessories",
        "accessories",
        row.name
      );
      let accessories_warehouse_df = frappe.meta.get_docfield(
        "Installation Accessories",
        "accessories_warehouse",
        row.name
      );
      accessories_df.read_only = 1;
      accessories_warehouse_df.read_only = 1;
      frm.refresh_fields();
    }
    if (row.accessories_type === "Internal") {
      let accessories_df = frappe.meta.get_docfield(
        "Installation Accessories",
        "accessories",
        row.name
      );
      let accessories_warehouse_df = frappe.meta.get_docfield(
        "Installation Accessories",
        "accessories_warehouse",
        row.name
      );
      accessories_df.read_only = 0;
      accessories_warehouse_df.read_only = 0;
      frm.refresh_fields();
    }
  }
);
