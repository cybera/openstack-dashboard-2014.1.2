from django.utils.translation import ugettext_lazy as _
import horizon
from openstack_dashboard.dashboards.project import dashboard


class DAIRShowback(horizon.Panel):
    name = _("Showback")
    slug = 'cloudtracker_showback'

dashboard.Project.register(DAIRShowback)
