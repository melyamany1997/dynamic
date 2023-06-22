frappe.views.calendar['Appointment'] = {
    field_map: {
        "start": "start",
        "end": "end",
        "id": "name",
        "title": "name",
        "allDay": "allDay",
    },


gantt: false,

get_events_method: "dynamic.ifi.api.get_events",

}

