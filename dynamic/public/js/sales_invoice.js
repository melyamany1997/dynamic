frappe.ui.form.on("Sales Invoice", {
  setup(frm) {
    frm.custom_make_buttons["Cheque"] = "Cheque";
  },
  domian_valid: function (frm) {
    var tera = false;
    frappe.call({
      method: "dynamic.dynamic.validation.get_active_domain_gebco",
      async: false,
      callback: function (r) {
        if (r.message) {
          tera = true;
        } else {
          tera = false;
        }
      },
    });
    return tera;
  },
  onload(frm) {
    var check_domain = frm.events.domian_valid();
    // console.log(check_domain)
    if (check_domain && frm.doc.docstatus == 0) {
      frm.add_custom_button(
        __("view Item Shortage"),
        function () {
          frappe.call({
            method: "dynamic.api.validate_active_domains_invocie",
            args: {
              doc: frm.doc.name,
            },
            callback: function (r) {
              console.log(r.message);
            },
          });
        },
        "view Item Shortage"
      );
    }
  },

  refresh(frm) {
    frm.events.add_cheque_button(frm);

    var check_domain = frm.events.domian_valid();
    if (check_domain && frm.doc.docstatus == 0) {
      frm.add_custom_button(
        __("view Item Shortage"),
        function () {
          frappe.call({
            method: "dynamic.api.validate_active_domains_invocie",
            args: {
              doc: frm.doc.name,
            },
            callback: function (r) {
              console.log(r.message);
            },
          });
        },
        "view Item Shortage"
      );
    }
    
  },


  add_cheque_button(frm) {
    if (frm.doc.docstatus == 1) {
      frappe.call({
        method: "dynamic.api.get_active_domains",
        callback: function (r) {
          if (r.message && r.message.length) {
            if (r.message.includes("Cheques")) {
              if (
                frm.doc.outstanding_amount != 0 &&
                !(cint(frm.doc.is_return) && frm.doc.return_against)
              ) {
                frm.add_custom_button(
                  __("Cheque"),
                  function () {
                    frm.events.make_cheque_doc(frm);
                  },
                  __("Create")
                );
              }
            }
          }
        },
      });
    }
  },
  make_cheque_doc(frm) {
    return frappe.call({
      method: "dynamic.cheques.doctype.cheque.cheque.make_cheque_doc",
      args: {
        dt: frm.doc.doctype,
        dn: frm.doc.name,
      },
      callback: function (r) {
        var doc = frappe.model.sync(r.message);
        frappe.set_route("Form", doc[0].doctype, doc[0].name);
      },
    });
  },
});
