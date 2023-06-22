from frappe import _

def get_data(data={}):
     dashboard_data =data
     dashboard_data["transactions"].append(
          {
                'label': _('LINE PARAMETER'),
                'items': ['LINE PARAMETER']
            },
     )
     return dashboard_data