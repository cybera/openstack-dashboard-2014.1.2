from django import conf
from django.utils.translation import ugettext_lazy as _
from horizon import tabs

from openstack_dashboard import api

import requests

class DAIRProjectUsageTab(tabs.Tab):
    name = _("Project Usage")
    slug = "project"
    template_name = "project/cloudtracker_usage/project_usage.html"
    preload = False

    def get_context_data(self, request):
        context = {}
        time = [
            (_('7 Days'), '7d'),
            (_('14 Days'), '14d'),
            (_('30 Days'), '30d'),
            (_('90 Days'), '90d'),
        ]
        queries = [
            (_('Instances'), 'project_allocated_instances'),
            (_('CPU'), 'project_allocated_cpu'),
            (_('Memory (Gb)'), 'project_allocated_memory'),
            (_('Ephemeral Disk (Gb)'), 'project_allocated_ephemeral_disk')
        ]

        context['time'] = time
        context['queries'] = queries
        context['request'] = self.request
        return context

class DAIRInstanceUsageTab(tabs.Tab):
    name =_("Instance Usage")
    slug = "instances"
    template_name = "project/cloudtracker_usage/instance_usage.html"
    preload = False

    def get_context_data(self, request):
        instances, foo = api.nova.server_list(self.request)

        context = {}
        time = [
            (_('7 Days'), '7d'),
            (_('14 Days'), '14d'),
            (_('30 Days'), '30d'),
            (_('90 Days'), '90d'),
        ]
        queries = [
            (_('CPU Time (Seconds)'), _('A sum of the number of seconds a CPU is active in a 5 minute period. A higher value denotes higher CPU usage.'),'instance_actual_cpu_time'),
            (_('Memory Usage'),_('The total amount of memory consumed by the instance.'), 'instance_actual_memory'),
            (_('Network (Bytes)'),_('The total bandwidth used in bytes. This does not differentiate between external or internal traffic.'), 'instance_actual_network_bytes'),
            (_('Disk Usage'),_('Size of the root disk.'),'instance_actual_disk_usage'),
            (_('Disk IO'), _('The number of input/output operations on a physical disk.'),'instance_actual_disk_io'),
        ]
        context['time'] = time
        context['queries'] = queries
        context['request'] = self.request
        context['instances'] = instances
        return context

class DAIRUsageTabs(tabs.TabGroup):
    slug = "cloudtracker_usage"
    tabs = (DAIRProjectUsageTab,DAIRInstanceUsageTab)
