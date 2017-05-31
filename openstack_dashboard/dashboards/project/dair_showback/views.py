from django.conf import settings
from django.template.defaultfilters import capfirst  # noqa
from django.template.defaultfilters import floatformat  # noqa
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView  # noqa
from django import http
from django.http import HttpResponse

from horizon.utils import csvbase
from horizon import forms
from horizon import tabs

from openstack_dashboard import api

import csv
import requests
import sys

class DAIRShowbackView(TemplateView):
    template_name = 'project/dair_showback/index.html'

    def get_context_data(self, **kwargs):
        context = super(DAIRShowbackView, self).get_context_data(**kwargs)
        context['form'] = forms.DateForm()
        project_id = self.request.user.tenant_id

        start_date = self.request.GET.get('start')
        context['start_date'] = start_date
        end_date = self.request.GET.get('end')
        context['end_date'] = end_date

        if start_date and end_date:
            usage = {}
            usage['Bandwidth'] = api.jt.get_dair_bandwidth_showback_usage(project_id, start_date, end_date)
            usage['Swift'] = api.jt.get_dair_object_store_showback_usage(project_id, start_date, end_date)
            usage['Instances'] = api.jt.get_dair_nova_showback_usage(project_id, start_date, end_date)
            usage['Snapshots'] = api.jt.get_dair_glance_showback_usage(project_id, start_date, end_date)
            usage['Volumes'] = api.jt.get_dair_cinder_showback_usage(project_id, start_date, end_date)
            context['usage'] = usage

        #    grand_total = usage['Instances']['total_cost']
        #    grand_total += usage['Snapshots']['total_cost']
        #    grand_total += usage['Volumes']['total_cost']
        #    context['grand_total'] = grand_total
        return context

class DAIRShowbackCSV_instancesView(TemplateView):
    def get(self, request, *args, **kwargs):
        project_id = self.request.user.tenant_id
        start_date = self.request.GET.get('start')
        end_date = self.request.GET.get('end')

        if start_date and end_date:
            usage = {}
            usage['Instances'] = api.jt.get_dair_nova_showback_usage(project_id, start_date, end_date)

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="instances-from-{0}-to-{1}.csv"'.format(start_date,end_date)
            w = csv.writer(response)
            w.writerow([_("Flavor"),_("Hours"),_("Quantity")])
            for k, v in usage['Instances'].iteritems():
               # if k == 'total_cost':
               #     continue
               #    w.writerow([k, v['hours'], v['count'], v['cost']])
                w.writerow([k, v['hours'], v['count']])

            return response

class DAIRShowbackCSV_bandwidthView(TemplateView):
    def get(self, request, *args, **kwargs):
        project_id = self.request.user.tenant_id
        start_date = self.request.GET.get('start')
        end_date = self.request.GET.get('end')

        if start_date and end_date:
            usage = {}
            usage['Bandwidth'] = api.jt.get_dair_bandwidth_showback_usage(project_id, start_date, end_date)

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="bandwidth-from-{0}-to-{1}.csv"'.format(start_date,end_date)
            w = csv.writer(response)
            w.writerow([_("In (Mb)"),_("Out (Mb)")])
            for k, v in usage['Bandwidth'].iteritems():
               # if k == 'total_cost':
               #     continue
               #    w.writerow([k, v['hours'], v['count'], v['cost']])
                w.writerow([ v['bytes_received'], v['bytes_transmitted']])

            return response

class DAIRShowbackCSV_swiftView(TemplateView):
    def get(self, request, *args, **kwargs):
        project_id = self.request.user.tenant_id
        start_date = self.request.GET.get('start')
        end_date = self.request.GET.get('end')

        if start_date and end_date:
            usage = {}
            usage['Swift'] = api.jt.get_dair_object_store_showback_usage(project_id, start_date, end_date)

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="object_store-from-{0}-to-{1}.csv"'.format(start_date,end_date)
            w = csv.writer(response)
            w.writerow([_("Space usage"),_("Container count"),_("Object count")])
            for k, v in usage['Swift'].iteritems():
                w.writerow([ v['space_usage'], v['container_count'], v['object_count']])

            return response

class DAIRShowbackCSV_snapshotsView(TemplateView):
    def get(self, request, *args, **kwargs):
        project_id = self.request.user.tenant_id
        start_date = self.request.GET.get('start')
        end_date = self.request.GET.get('end')

        if start_date and end_date:
            usage = {}
            usage['Snapshots'] = api.jt.get_dair_glance_showback_usage(project_id, start_date, end_date)

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="snapshots-from-{0}-to-{1}.csv"'.format(start_date,end_date)
            w = csv.writer(response)
            w.writerow([_("Name"),_("Hours"),_("Size (GB)")])
            for k, v in usage['Snapshots'].iteritems():
            #    if k == 'total_cost':
            #        continue
            #    w.writerow([k, v['hours'], v['size'], v['cost']])
                w.writerow([k, v['hours'], v['size']])

            return response

class DAIRShowbackCSV_volumesView(TemplateView):
    def get(self, request, *args, **kwargs):
        project_id = self.request.user.tenant_id
        start_date = self.request.GET.get('start')
        end_date = self.request.GET.get('end')

        if start_date and end_date:
            usage = {}
            usage['Volumes'] = api.jt.get_dair_cinder_showback_usage(project_id, start_date, end_date)

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="volumes-from-{0}-to-{1}.csv"'.format(start_date,end_date)
            w = csv.writer(response)
            w.writerow([_("Name"),_("Hours"),_("Size (GB)")])
            for k, v in usage['Volumes'].iteritems():
            #    if k == 'total_cost':
            #        continue
            #    w.writerow([k, v['hours'], v['size'], v['cost']])
                w.writerow([k, v['hours'], v['size']])

            return response

class WarningView(TemplateView):
    template_name = "project/_warning.html"
