
from frappe import _
from frappe import get_active_domains
DOMAINS = get_active_domains()


def get_data(data={}):
    if "Terra" in DOMAINS:
        data['non_standard_fieldnames'].update(
            {'Actions': "customer",'Appointment': "party"}
            )
        data['transactions'].append(
            {
                'label': _('Actions'),
                'items': ['Appointment',"Actions"]
            }
        )
    return data
