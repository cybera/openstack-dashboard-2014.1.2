from django.utils.translation import ugettext_lazy as _
import horizon
from openstack_dashboard.dashboards.project import dashboard


class DAIRUsage(horizon.Panel):
    name = _("Usage Graphs")
    slug = 'cloudtracker_usage'

dashboard.Project.register(DAIRUsage)
