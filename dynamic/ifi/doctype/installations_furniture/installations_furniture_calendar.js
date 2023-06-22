
// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.views.calendar["Installations Furniture"] = {
		field_map: {
			"start": "start",
			"end": "end",
			"id": "name",
			"title": "desc2",
			"allDay": "allDay",
		},

	// style_map: {
	// 	"0": "info",
	// 	"1": "standard",
	// 	"2": "danger"
	// },
	gantt: true,
	// gantt: {
	// 	field_map: {
	// 		"start": "from_time",
	// 		"end": "to_time",
	// 		"id": "team",
	// 	"description":"team",
	// 	"subtitle":"team",
	// 	"details-container":"team",
	// 		"title": "name",
	// 		"allDay": "allDay"
	// 	}
	// },
	filters: [
		{
			"fieldtype": "Link",
			"fieldname": "sales_order",
			"options": "Sales Order",
			"label": __("Sales Order")
		},
	],
	get_events_method: "dynamic.ifi.doctype.installations_furniture.installations_furniture.get_events",
	get_css_class: function(data) {
        // console.log(data)
		// test()
		if(data.ref_status=="Pending") {
			return "success";
		} if(data.ref_status=="Start") {
			return "danger";
		} else if(data.ref_status=="Inprogress") {
			return "warning";
		} else if(data.ref_status=="Completed") {
			return "extra-light";
		}
	},
}

function test(data){
	console.log(4444)
	// data
}


// realtiv

// frappe.views.Calendar = frappe.views.Calendar.extend({

// 	init: function(options) {
// 	  options.page.custom_actions.removeClass('hidden-md');
// 	  options.page.custom_actions.find('.sort-selector').addClass('hidden-md');
// 	  //options.page.sort_selector.addClass('hidden-md');
  
// 	  this._super(options);
// 	  if (this.list_view.calendar_name=='Installations Furniture') {
// 		this.get_events_method='dynamic.ifi.doctype.installations_furniture.installations_furniture.get_events';
// 		this.field_map = {
// 				"start": "planned_start_date",
// 				"end": "planned_end_date",
// 				"title": "name",
// 				"customer":"customer",
// 				"team":"team",
// 				"allDay": "allDay"
// 			},
  
// 		this.filters = [
// 					{
// 						"fieldtype": "Link",
// 						"fieldname": "sales_order",
// 						"options": "Sales Order",
// 						"label": __("Sales Order")
// 					},
// 		];
// 		// this.update_event_method='jobcard_planning.controllers.jobcard_planning.update_jobcard_planned_date';
// 	   }
// 	  },
  
// 	// update_event: function(event, revertFunc) {
// 	//   if (this.list_view.calendar_name=='Installations Furniture') {
// 	// 	event.color='#0ecbb1';
// 	// 	event.backgroundColor='#0ecbb1';
// 	// 	this.$cal.fullCalendar("updateEvent",event);
// 	//   }
// 	//   this._super(event, revertFunc);
// 	// }
//   })