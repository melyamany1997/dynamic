frappe.listview_settings["Device"] = {
  add_fields: ["status"],
  get_indicator: function (doc) {
    if (doc.status == "Connected") {
      return [__(doc.status), "green", "status,=," + doc.status];
    } else if (doc.status == "Disonnected") {
      return [__(doc.status), "red", "status,=," + doc.status];
    }
  },
  onload: function (list_view) {
    get_device_Status(list_view);
    list_view.page
      .add_inner_button(__("Refresh Device Status"), function () {
        // debugger
        get_device_Status(list_view,true);
      })
      .addClass("btn-primary");
  },
};
function get_device_Status(list_view,freeze=false) {
  frappe.call({
    method: "dynamic.dynamic_hr.doctype.device.device.get_device_status",
    freeze: freeze,
    callback: function (r) {
      // frappe.msgprint(__("Done"));
      // frappe.hide_progress();
      list_view.refresh();
    },
  });
}
