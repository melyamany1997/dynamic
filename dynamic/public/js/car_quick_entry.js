frappe.provide("frappe.ui.form");

frappe.ui.form.CarQuickEntryForm = class CarQuickEntryForm extends (
  frappe.ui.form.QuickEntryForm
) {
  constructor(doctype, after_insert, init_callback, doc, force) {
    super(doctype, after_insert, init_callback, doc, force);
    this.skip_redirect_on_error = true;
  }

  render_dialog() {
    console.log(this)
    this.mandatory.find((x) => x.fieldname == "serial_no").get_query = () => {
      return {
        query: "dynamic.gebco.doctype.car.car.get_serial_no_query",
        filters: { docname: this.doc.name },
      };
    };
    super.render_dialog();
  }

  get_variant_fields() {
    var variant_fields = [
      {
        fieldtype: "Section Break",
        label: __("Primary Contact Details"),
        collapsible: 1,
      },
      {
        label: __("Test Serial"),
        fieldname: "test_Serial",
        fieldtype: "Data",
      },
    ];

    return variant_fields;
  }
};
