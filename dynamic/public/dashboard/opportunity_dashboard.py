
from frappe import _
from frappe import get_active_domains
DOMAINS = get_active_domains()


def get_data(data={}):
    if "Terra" in DOMAINS:
       
        data['transactions'].append(
            {
                'label': _('Sales Order'),
                'items': ['Sales Order']
            }
        )
    return data
