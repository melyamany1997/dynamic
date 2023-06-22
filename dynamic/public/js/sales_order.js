
{% include 'erpnext/selling/sales_common.js' %}


frappe.ui.form.on("Sales Order", {
  // validate: function(frm) {
  //   console.log('validate1111111111111111')
  //   frappe.call({
  //     method: "dynamic.api.check_source_item",
  //     args:{
  //       self:frm.doc,
  //     },
  //     callback: function(r) {
  //      console.log(r.message)
  //     }
  // });
  // },
 
  setup:function(frm) {
    frm.events.domian_valid(frm)
    frm.events.update_grid(frm)
    frm.custom_make_buttons = {
      "Installation Request": "Installation Request",
      "Cheque": "Cheque",
    };
  },
  refresh: function (frm) {  
    frappe.call({
      method: "dynamic.api.get_active_domains",
      callback: function (r) {
        if (r.message.includes("Terra") && frm.doc.docstatus == 2) {
            frm.page.clear_primary_action();  
        }
      }
    })
    frm.events.add_cheque_button(frm);
    frm.events.add_installation_button(frm);
    frm.events.add_furniture_installation_button(frm);
    cur_frm.page.remove_inner_button(__('Update Items'))
    if(frm.doc.docstatus === 1 && frm.doc.status !== 'Closed'
			&& flt(frm.doc.per_delivered, 6) < 100 && flt(frm.doc.per_billed, 6) < 100) {
			frm.add_custom_button(__('Update Items'), () => {
        erpnext.utils.update_child_items({
					frm: frm,
					child_docname: "items",
					child_doctype: "Sales Order Detail",
					cannot_add_row: true,
				})
			});
		}
  },
  get_advancess:function(frm){
    if(!frm.is_return) {
			frappe.call({
        method: "dynamic.api.get_active_domains",
        callback: function (r) {
          if (r.message && r.message.length) {
            if (r.message.includes("IFI")) {
              return frappe.call({
                method: "dynamic.ifi.api.get_advanced_so_ifi",//get_advanced_so_ifi
                args:{
                  doc_name: frm.doc.name,
                },
                callback: function(r, rt) {
                  r.message.forEach(row => {
                    // console.log(row)
                    let child = frm.add_child("advancess");
                    child.reference_type = row.reference_type,
                    child.reference_name = row.reference_name,
                    child.reference_row = row.reference_row,
                    child.remarks = row.remarks,
                    child.advance_amount = flt(row.amount),
                    child.allocated_amount = row.allocated_amount,
                    child.ref_exchange_rate = flt(row.exchange_rate)
                  });
                  refresh_field("advancess");
                }
              })
            }
        }}
    })

      
		}
  },
  
  opportunity:function(frm){
    if (frm.doc.opportunity){
      frappe.call({
        method :"dynamic.api.get_active_domains" ,
        async: false,
        callback:function (r){
         if (r.message.includes("Terra")) {
          frappe.call({
            method: "frappe.client.get_value",
            args: {
              doctype: "Opportunity",
              fieldname: "source",
              filters: {
                name: frm.doc.opportunity
              }
            },
            callback: function(data) {
              if (data.message) {
                frm.set_value("source", data.message.source);
                frm.refresh_field("source")
              }
            }
          });
          }
        }
    })
    }
  },
  onload: function (frm) {
    frm.set_query('item_purchase_order', 'items', function(doc, cdt, cdn) {
      let row = locals[cdt][cdn];
			return {
				query: 'dynamic.api.get_purchase_order',
				filters:{"item_code":row.item_code}
			};
		});
  },
  update_grid:function(frm){
    frappe.call({
      method: "dynamic.api.get_active_domains",
      callback: function (r) {
        if (r.message && r.message.length) {
          if (r.message.includes("IFI")) {
            frm.get_field('items').grid.editable_fields = [
              {fieldname: 'item_code', columns: 1},
              // {fieldname: 'item_name', columns: 1},
              {fieldname: 'qty', columns: 1},
              {fieldname: 'rate', columns: 1},
              {fieldname: 'amount', columns: 1},
              {fieldname: 'supplier', columns: 1}
            ];
          }
      }}
  })
  },



  total_cars: function (frm) {
    if (frm.doc.total_cars) {
      frm.set_value("pending_cars", frm.doc.total_cars);
      frm.set_value("not_requested_cars", frm.doc.total_cars);
    }
  },


  add_cheque_button(frm) {
    console.log("test--->")
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
  add_installation_button(frm) {
    if (frm.doc.docstatus == 1) {
      frappe.call({
        method: "dynamic.api.get_active_domains",
        callback: function (r) {
          if (r.message && r.message.length) {
            if (r.message.includes("Gebco")) {
              frm.add_custom_button(
                __("Installation Request"),
                function () {
                  frm.events.make_installation_request(frm);
                },
                __("Create")
              );
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
  make_installation_request(frm) {
    frappe.model.open_mapped_doc({
      // installation_request_doc 
      method: "dynamic.gebco.api.create_installation_request",
      frm: frm,
    });
  },
  set_warehouse: function (frm) {
    frm.events.autofill_warehouse(
      frm,
      frm.doc.items,
      "item_warehouse",
      frm.doc.set_warehouse
    );
  },
  purchase_order: function (frm) {
    frm.events.autofill_purchase_order(
      frm,
      frm.doc.items,
      "item_purchase_order",
      frm.doc.purchase_order
    );
  },
  autofill_warehouse: function (frm, child_table, warehouse_field, warehouse) {
    if (warehouse && child_table && child_table.length) {
      let doctype = child_table[0].doctype;
      $.each(child_table || [], function (i, item) {
        frappe.model.set_value(doctype, item.name, warehouse_field, warehouse);
      });
    }
  },
  autofill_purchase_order: function (
    frm,
    child_table,
    warehouse_field,
    warehouse
  ) {
    if (warehouse && child_table && child_table.length) {
      let doctype = child_table[0].doctype;
      $.each(child_table || [], function (i, item) {
        frappe.model.set_value(doctype, item.name, warehouse_field, warehouse);
      });
    }
  },

  domian_valid: function (frm) {
    if(cur_frm.doc.docstatus === 1){
      frappe.call({
        method :"dynamic.api.get_active_domains" ,
        async: false,
        callback:function (r){
         if (r.message.includes("Terra")) {
          cur_frm.cscript['make_sales_invoice'] = create_terra_sales_invoice
            cur_frm.page.remove_inner_button(__('Update Items'))
            }
        }
    })
    }
 } ,
update_child_items : function(frm,child_docname,child_doctype,cannot_add_row) {
	var cannot_add_row = (typeof cannot_add_row === 'undefined') ? true : cannot_add_row;
	var child_docname = (typeof cannot_add_row === 'undefined') ? "items" : child_docname;
	var child_meta = frappe.get_meta(`${frm.doc.doctype} Item`);

	const get_precision = (fieldname) => child_meta.fields.find(f => f.fieldname == fieldname).precision;

	this.data = [];
	const fields = [{
		fieldtype:'Data',
		fieldname:"docname",
		read_only: 1,
		hidden: 1,
	}, {
		fieldtype:'Link',
		fieldname:"item_code",
		options: 'Item',
		in_list_view: 1,
		read_only: 0,
		disabled: 0,
		label: __('Item Code'),
		get_query: function() {
			let filters;
			if (frm.doc.doctype == 'Sales Order') {
				filters = {"is_sales_item": 1};
			} else if (frm.doc.doctype == 'Purchase Order') {
				if (frm.doc.is_subcontracted == "Yes") {
					filters = {"is_sub_contracted_item": 1};
				} else {
					filters = {"is_purchase_item": 1};
				}
			}
			return {
				query: "erpnext.controllers.queries.item_query",
				filters: filters
			};
		}
	}, {
		fieldtype:'Link',
		fieldname:'uom',
		options: 'UOM',
		read_only: 0,
		label: __('UOM'),
		reqd: 1,
		onchange: function () {
			frappe.call({
				method: "erpnext.stock.get_item_details.get_conversion_factor",
				args: { item_code: this.doc.item_code, uom: this.value },
				callback: r => {
					if(!r.exc) {
						if (this.doc.conversion_factor == r.message.conversion_factor) return;

						const docname = this.doc.docname;
						dialog.fields_dict.trans_items.df.data.some(doc => {
							if (doc.docname == docname) {
								doc.conversion_factor = r.message.conversion_factor;
								dialog.fields_dict.trans_items.grid.refresh();
								return true;
							}
						})
					}
				}
			});
		}
	}, {
		fieldtype:'Float',
		fieldname:"qty",
		default: 0,
		read_only: 0,
		in_list_view: 1,
		label: __('Qty'),
		precision: get_precision("qty")
	}, {
		fieldtype:'Currency',
		fieldname:"rate",
		options: "currency",
		default: 0,
		read_only: 0,
		in_list_view: 1,
		label: __('Rate'),
		precision: get_precision("rate")
	}];

	if (frm.doc.doctype == 'Sales Order' || frm.doc.doctype == 'Purchase Order' ) {
		fields.splice(2, 0, {
			fieldtype: 'Date',
			fieldname: frm.doc.doctype == 'Sales Order' ? "delivery_date" : "schedule_date",
			in_list_view: 1,
			label: frm.doc.doctype == 'Sales Order' ? __("Delivery Date") : __("Reqd by date"),
			reqd: 1
		})
		fields.splice(3, 0, {
			fieldtype: 'Float',
			fieldname: "conversion_factor",
			in_list_view: 1,
			label: __("Conversion Factor"),
			precision: get_precision('conversion_factor')
		})
	}

	const dialog = new frappe.ui.Dialog({
		title: __("Update Items"),
		fields: [
			{
				fieldname: "trans_items",
				fieldtype: "Table",
				label: "Items",
				cannot_add_rows: cannot_add_row,
				in_place_edit: false,
				reqd: 1,
				data: this.data,
				get_data: () => {
					return this.data;
				},
				fields: fields
			},
		],
		primary_action: function() {
			const trans_items = this.get_values()["trans_items"].filter((item) => !!item.item_code);
			frappe.call({
				method: 'erpnext.controllers.accounts_controller.update_child_qty_rate',
				freeze: true,
				args: {
					'parent_doctype': frm.doc.doctype,
					'trans_items': trans_items,
					'parent_doctype_name': frm.doc.name,
					'child_docname': child_docname
				},
				callback: function() {
					frm.reload_doc();
				}
			});
			this.hide();
			refresh_field("items");
		},
		primary_action_label: __('Update')
	});

	frm.doc[child_docname].forEach(d => {
		dialog.fields_dict.trans_items.df.data.push({
			"docname": d.name,
			"name": d.name,
			"item_code": d.item_code,
			"delivery_date": d.delivery_date,
			"schedule_date": d.schedule_date,
			"conversion_factor": d.conversion_factor,
			"qty": d.qty,
			"rate": d.rate,
			"uom": d.uom
		});
		this.data = dialog.fields_dict.trans_items.df.data;
		dialog.fields_dict.trans_items.grid.refresh();
	})
	dialog.show();
},

add_furniture_installation_button(frm) {
  if (frm.doc.docstatus == 1) {
    frappe.call({
      method: "dynamic.api.get_active_domains",
      callback: function (r) {
        if (r.message && r.message.length) {
          if (r.message.includes("IFI")) {
            frm.add_custom_button(
              __("Installation Furniture Order"),
              function () {
                frm.events.make_furniture_installation_order(frm);
              },
              __("Create")
            );
          }
        }
      },
    });
  }
},

make_furniture_installation_order(frm) {
  frappe.model.open_mapped_doc({
    // installation_request_doc
    method: "dynamic.ifi.api.create_furniture_installation_order",
    frm: frm,

  });
  
},

});

frappe.ui.form.on("Sales Order Item", { 
  item_warehouse: function (frm, cdt, cdn) {
    var row = frappe.get_doc(cdt, cdn);
    frappe.model.set_value(cdt, cdn, "warehouse", row.item_warehouse);
  },
  supplier:function(frm,cdt,cdn){
    frappe.call({
      method: "dynamic.api.get_active_domains",
      callback: function (r) {
        if (r.message && r.message.length) {
          if (r.message.includes("IFI")) {
            let row = locals[cdt][cdn]
            if(row.supplier){
              row.delivered_by_supplier = 1
            }
            else if(!row.supplier){
              row.delivered_by_supplier = 0

            }
            frm.refresh()
          }
        }
      }
    })
    
  }
  
 
});

frappe.ui.form.on(
  "Sales Order Item",
  "item_purchase_order",
  function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (row.item_purchase_order && row.item_code) {
      frappe.call({
        method: "dynamic.api.check_delivery_warehosue",
        args: {
          doc_name: row.item_purchase_order,
          item_code: row.item_code,
          warehouse: row.warehouse,
        },
        callback: function (r) {
          if (r.message){
            // console.log('warehouse -> ',r.message)
            row.warehouse = r.message;
            frm.refresh_fields();
          }
        },
      });
    }
  }
);


var create_terra_sales_invoice = function() {

  frappe.model.open_mapped_doc({
  method: "dynamic.terra.doctype.sales_order.sales_order.make_sales_invoice",
  frm: cur_frm
})
}

var create_ifi_purchase_order = function() {
  let pending_items = cur_frm.doc.items.some((item) =>{
    let pending_qty = flt(item.stock_qty) - flt(item.ordered_qty);
    return pending_qty > 0;
  })
  if(!pending_items){
    frappe.throw({message: __("Purchase Order already created for all Sales Order items"), title: __("Note")});
  }

  var me = this;
  var dialog = new frappe.ui.Dialog({
    title: __("Select Items"),
    size: "large",
    fields: [
      {
        "fieldtype": "Check",
        "label": __("Against Default Supplier"),
        "fieldname": "against_default_supplier",
        "default": 0
      },
      {
        fieldname: 'items_for_po', fieldtype: 'Table', label: 'Select Items',
        fields: [
          {
            fieldtype:'Data',
            fieldname:'item_code',
            label: __('Item'),
            read_only:1,
            in_list_view:1
          },
          {
            fieldtype:'Data',
            fieldname:'item_name',
            label: __('Item name'),
            read_only:1,
            in_list_view:1
          },
          {
            fieldtype:'Float',
            fieldname:'pending_qty',
            label: __('Pending Qty'),
            read_only: 1,
            in_list_view:1
          },
          {
            fieldtype:'Link',
            read_only:1,
            fieldname:'uom',
            label: __('UOM'),
            in_list_view:1,
          },
          {
            fieldtype:'Data',
            fieldname:'supplier',
            label: __('Supplier'),
            read_only:1,
            in_list_view:1
          },
        ]
      }
    ],
    primary_action_label: 'Create Purchase Order',
    primary_action (args) {
      if (!args) return;

      let selected_items = dialog.fields_dict.items_for_po.grid.get_selected_children();
      if(selected_items.length == 0) {
        frappe.throw({message: 'Please select Items from the Table', title: __('Items Required'), indicator:'blue'})
      }

      dialog.hide();

      var method = args.against_default_supplier ? "make_purchase_order_for_default_supplier" : "make_purchase_order"
      return frappe.call({
        method: "erpnext.selling.doctype.sales_order.sales_order." + method,
        freeze: true,
        freeze_message: __("Creating Purchase Order ..."),
        args: {
          "source_name": cur_frm.doc.name,
          "selected_items": selected_items
        },
        freeze: true,
        callback: function(r) {
          if(!r.exc) {
            if (!args.against_default_supplier) {
              frappe.model.sync(r.message);
              frappe.set_route("Form", r.message.doctype, r.message.name);
            }
            else {
              frappe.route_options = {
                "sales_order": cur_frm.doc.name
              }
              frappe.set_route("List", "Purchase Order");
            }
          }
        }
      })
    }
  });

  dialog.fields_dict["against_default_supplier"].df.onchange = () => set_po_items_data(dialog);

  function set_po_items_data (dialog) {
    var against_default_supplier = dialog.get_value("against_default_supplier");
    var items_for_po = dialog.get_value("items_for_po");

    if (against_default_supplier) {
      let items_with_supplier = items_for_po.filter((item) => item.supplier)

      dialog.fields_dict["items_for_po"].df.data = items_with_supplier;
      dialog.get_field("items_for_po").refresh();
    } else {
      let po_items = [];
      cur_frm.doc.items.forEach(d => {
        let ordered_qty = cur_frm.get_ordered_qty(d, cur_frm.doc);
        let pending_qty = (flt(d.stock_qty) - ordered_qty) / flt(d.conversion_factor);
        if (pending_qty > 0) {
          po_items.push({
            "doctype": "Sales Order Item",
            "name": d.name,
            "item_name": d.item_name,
            "item_code": d.item_code, 
            "pending_qty": pending_qty,
            "uom": d.uom,
            "supplier": d.supplier
          });
        }
      });

      dialog.fields_dict["items_for_po"].df.data = po_items;
      dialog.get_field("items_for_po").refresh();
    }
  }

  set_po_items_data(dialog);
  dialog.get_field("items_for_po").grid.only_sortable();
  dialog.get_field("items_for_po").refresh();
  dialog.wrapper.find('.grid-heading-row .grid-row-check').click();
  dialog.show();
}



const extend_sales_order = erpnext.selling.SalesOrderController.extend({

  refresh: function(doc, dt, dn) {
    var me = this;
		this._super(doc);
    if(doc.status !== 'Closed') {
      if(doc.status !== 'On Hold') {
        frappe.call({
          method: "dynamic.api.get_active_domains",
          callback: function (r) {
            if (r.message && r.message.length) {
              if (r.message.includes("IFI")){
                // Make Purchase Order
                if (!cur_frm.doc.is_internal_customer) {
                  cur_frm.cscript['make_sales_invoice'] = create_ifi_sales_invoice
                  cur_frm.page.remove_inner_button('Purchase Order', 'Create')
                  cur_frm.add_custom_button(__('Purchase Order'), () => me.frm.trigger("make_purchase_order_ifi"), __('Create'));
                }
              }
              if(r.message.includes("Kmina")){
                // sales invoice
              if(flt(doc.per_billed, 6) < 100) {
                // cur_frm.page.remove_inner_button('Sales Invoice', 'Create')
                cur_frm.cscript['make_sales_invoice'] = create_kmina_sales_invoice //new

                // cur_frm.add_custom_button(__('Sales Invoice'), () => me.frm.trigger("make_sales_invoice"), __('Create'));
              }
              }
            }
          }
        })

      }
    }
  },
  make_purchase_order_ifi: function(){
		let pending_items = this.frm.doc.items.some((item) =>{
			let pending_qty = flt(item.stock_qty) - flt(item.ordered_qty);
			return pending_qty > 0;
		})
		if(!pending_items){
			frappe.throw({message: __("Purchase Order already created for all Sales Order items"), title: __("Note")});
		}

		var me = this;
		var dialog = new frappe.ui.Dialog({
			title: __("Select Items"),
			size: "large",
			fields: [
				{
					"fieldtype": "Check",
					"label": __("Against Default Supplier"),
					"fieldname": "against_default_supplier",
					"default": 0
				},
				{
					fieldname: 'items_for_po', fieldtype: 'Table', label: 'Select Items',
					fields: [
						{
							fieldtype:'Data',
							fieldname:'item_code',
							label: __('Item'),
							read_only:1,
							in_list_view:1
						},
						{
							fieldtype:'Data',
							fieldname:'item_name',
							label: __('Item name'),
							read_only:1,
							in_list_view:1
						},
						{
							fieldtype:'Float',
							fieldname:'pending_qty',
							label: __('Pending Qty'),
							read_only: 1,
							in_list_view:1
						},
						{
							fieldtype:'Link',
							read_only:1,
							fieldname:'uom',
							label: __('UOM'),
							in_list_view:1,
						},
						{
							fieldtype:'Data',
							fieldname:'supplier',
							label: __('Supplier'),
							read_only:1,
							in_list_view:1
						},
					]
				}
			],
			primary_action_label: 'Create Purchase Order',
			primary_action (args) {
				if (!args) return;

				let selected_items = dialog.fields_dict.items_for_po.grid.get_selected_children();
				if(selected_items.length == 0) {
					frappe.throw({message: 'Please select Items from the Table', title: __('Items Required'), indicator:'blue'})
				}

				dialog.hide();
        // dynamic.ifi.api.override_make_purchase_order **
				var method = '' //args.against_default_supplier ? "make_purchase_order_for_default_supplier" : "override_make_purchase_order"
        if(args.against_default_supplier){
          method= "erpnext.selling.doctype.sales_order.sales_order.make_purchase_order_for_default_supplier"
        }else{
          method= "dynamic.ifi.api.override_make_purchase_order"
        }
				return frappe.call({
					method:  method,
					freeze: true,
					freeze_message: __("Creating Purchase Order ..."),
					args: {
						"source_name": me.frm.doc.name,
						"selected_items": selected_items
					},
					freeze: true,
					callback: function(r) {
						if(!r.exc) {
							if (!args.against_default_supplier) {
								frappe.model.sync(r.message);
								frappe.set_route("Form", r.message.doctype, r.message.name);
							}
							else {
								frappe.route_options = {
									"sales_order": me.frm.doc.name
								}
								frappe.set_route("List", "Purchase Order");
							}
						}
					}
				})
			}
		});

		dialog.fields_dict["against_default_supplier"].df.onchange = () => set_po_items_data(dialog);

		function set_po_items_data (dialog) {
			var against_default_supplier = dialog.get_value("against_default_supplier");
			var items_for_po = dialog.get_value("items_for_po");

			if (against_default_supplier) {
				let items_with_supplier = items_for_po.filter((item) => item.supplier)

				dialog.fields_dict["items_for_po"].df.data = items_with_supplier;
				dialog.get_field("items_for_po").refresh();
			} else {
				let po_items = [];
				me.frm.doc.items.forEach(d => {
					let ordered_qty = me.get_ordered_qty(d, me.frm.doc);
					let pending_qty = (flt(d.stock_qty) - ordered_qty) / flt(d.conversion_factor);
					if (pending_qty > 0) {
						po_items.push({
							"doctype": "Sales Order Item",
							"name": d.name,
							"item_name": d.item_name,
							"item_code": d.item_code,
							"pending_qty": pending_qty,
							"uom": d.uom,
							"supplier": d.supplier
						});
					}
				});

				dialog.fields_dict["items_for_po"].df.data = po_items;
				dialog.get_field("items_for_po").refresh();
			}
		}

		set_po_items_data(dialog);
		dialog.get_field("items_for_po").grid.only_sortable();
		dialog.get_field("items_for_po").refresh();
		dialog.wrapper.find('.grid-heading-row .grid-row-check').click();
		dialog.show();
	},
  // make_sales_invoice: function() {
	// 	frappe.model.open_mapped_doc({
	// 		method: "dynamic.kmina.api.make_sales_invoice",
	// 		frm: this.frm
	// 	})
	// },
})
var create_kmina_sales_invoice = function() {
  frappe.model.open_mapped_doc({
  method: "dynamic.kmina.api.make_sales_invoice",
  frm: cur_frm
})
}

var create_ifi_sales_invoice = function() {
  frappe.model.open_mapped_doc({
  method: "dynamic.ifi.api.ifi_make_sales_invoice",
  frm: cur_frm
})
}
$.extend(
	cur_frm.cscript,
	new extend_sales_order({frm: cur_frm}),
);