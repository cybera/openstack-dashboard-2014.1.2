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

import xlwt
import csv
import requests
import sys

class DAIRShowbackView(TemplateView):
    template_name = 'project/cloudtracker_showback/index.html'

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
            response['Content-Disposition'] = 'attachment; filename="{0}-{1}-{2}-{3}.csv"'.format(_("instances-from"),start_date,_("to"),end_date)
            w = csv.writer(response)
            w.writerow([_("Flavor"),_("Hours"),_("Quantity")])
            if (type(usage['Instances'])  == type(dict())):
                for k, v in usage['Instances'].iteritems():
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
            response['Content-Disposition'] = 'attachment; filename="{0}-{1}-{2}-{3}.csv"'.format((_("bandwidth-from")).encode('utf-8'),start_date,_("to"),end_date)
            w = csv.writer(response)
            w.writerow([_("In (Mb)"),_("Out (Mb)")])
            if (type(usage['Bandwidth'])  == type(dict())):
                for k, v in usage['Bandwidth'].iteritems():
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
            response['Content-Disposition'] = 'attachment; filename="{0}-{1}-{2}-{3}.csv"'.format(_("object_storage-from"),start_date,_("to"),end_date)
            w = csv.writer(response)

            w.writerow([_("Space usage"),_("Container count"),_("Object count")])
            if (type(usage['Swift'])  == type(dict())):
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
            response['Content-Disposition'] = 'attachment; filename="{0}-{1}-{2}-{3}.csv"'.format(_("snapshots-from"),start_date,_("to"),end_date)
            w = csv.writer(response)
            w.writerow([_("Name"),_("Hours"),_("Size (GB)")])
            if (type(usage['Snapshots'])  == type(dict())):
                for k, v in usage['Snapshots'].iteritems():
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
            response['Content-Disposition'] = 'attachment; filename="{0}-{1}-{2}-{3}.csv"'.format(_("volumes-from"),start_date,_("to"),end_date)
            w = csv.writer(response)
            w.writerow([_("Name"),_("Hours"),_("Size (GB)")])
            if (type(usage['Volumes'])  == type(dict())):
                for k, v in usage['Volumes'].iteritems():
                    w.writerow([k, v['hours'], v['size']])

            return response

class DAIRShowbackCSV_SummaryView(TemplateView):
    def get(self, request, *args, **kwargs):
        project_id = self.request.user.tenant_id
        start_date = self.request.GET.get('start')
        end_date = self.request.GET.get('end')

        if start_date and end_date:
            usage = {}
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="{0}-{1}-{2}-{3}.csv"'.format(_("summary-from"),start_date,_("to"),end_date)
            w = csv.writer(response)

            usage['Instances'] = api.jt.get_dair_nova_showback_usage(project_id, start_date, end_date)
            w.writerow([_("Instances")])
            w.writerow([_("Flavor"),_("Hours"),_("Quantity")])
            if (type(usage['Instances'])  == type(dict())):
                for k, v in usage['Instances'].iteritems():
                    w.writerow([k, v['hours'], v['count']])
            w.writerow([_(" ")])
            w.writerow([(_("External Bandwidth")).encode('utf-8')])
            usage['Bandwidth'] = api.jt.get_dair_bandwidth_showback_usage(project_id, start_date, end_date)
            w.writerow([_("In (Mb)"),_("Out (Mb)")])
            if (type(usage['Bandwidth'])  == type(dict())):
                for k, v in usage['Bandwidth'].iteritems():
                    w.writerow([ v['bytes_received'], v['bytes_transmitted']])
            usage['Snapshots'] = api.jt.get_dair_glance_showback_usage(project_id, start_date, end_date)
            w.writerow([_(" ")])
            w.writerow([_("Snapshots")])
            w.writerow([_("Name"),_("Hours"),_("Size (GB)")])
            if (type(usage['Snapshots'])  == type(dict())):
                for k, v in usage['Snapshots'].iteritems():
                    w.writerow([k, v['hours'], v['size']])
            w.writerow([_(" ")])
            w.writerow([_("Volumes")])
            usage['Volumes'] = api.jt.get_dair_cinder_showback_usage(project_id, start_date, end_date)
            w.writerow([_("Name"),_("Hours"),_("Size (GB)")])
            if (type(usage['Volumes'])  == type(dict())):
                for k, v in usage['Volumes'].iteritems():
                    w.writerow([k, v['hours'], v['size']])
            usage['Swift'] = api.jt.get_dair_object_store_showback_usage(project_id, start_date, end_date)
            w.writerow([_(" ")])
            w.writerow([_("Object Storage")])
            w.writerow([_("Space usage"),_("Container count"),_("Object count")])
            if (type(usage['Swift'])  == type(dict())):
                for k, v in usage['Swift'].iteritems():
                    w.writerow([ v['space_usage'], v['container_count'], v['object_count']])
            return response

class DAIRShowbackXML_SummaryView(TemplateView):
    def get(self, request, *args, **kwargs):
        project_id = self.request.user.tenant_id
        start_date = self.request.GET.get('start')
        end_date = self.request.GET.get('end')

        header_font = xlwt.Font()
        header_font.bold = True
        # Define the header styles
        table_header = xlwt.XFStyle()
        table_header.font = header_font

        if start_date and end_date:
            usage = {}
            wb = xlwt.Workbook()
            ws_i = wb.add_sheet(_('Instances'))
            first_col = ws_i.col(0)
            first_col.width = 256 * 20
            usage['Instances'] = api.jt.get_dair_nova_showback_usage(project_id, start_date, end_date)
            ws_i.write(0,0,_("Flavor"), table_header)
            ws_i.write(0,1,_("Hours"), table_header)
            ws_i.write(0,2,_("Quantity"), table_header)
            row=1
            if (type(usage['Instances'])  == type(dict())):
                for k, v in usage['Instances'].iteritems():
                    ws_i.write(row,0, k)
                    ws_i.write(row,1, v['hours'])
                    ws_i.write(row,2, v['count'])
                    row +=1
            ws_b = wb.add_sheet(_('External Bandwidth'))
            usage['Bandwidth'] = api.jt.get_dair_bandwidth_showback_usage(project_id, start_date, end_date)
            ws_b.write(0,0,_("In (Mb)"), table_header)
            ws_b.write(0,1,_("Out (Mb)"), table_header)
            row=1
            if (type(usage['Bandwidth'])  == type(dict())):
                for k, v in usage['Bandwidth'].iteritems():
                    ws_b.write(row,0, v['bytes_received'])
                    ws_b.write(row,1, v['bytes_transmitted'])
                    row +=1
            ws_s = wb.add_sheet(_('Snapshots'))
            first_col = ws_s.col(0)
            first_col.width = 256 * 50
            usage['Snapshots'] = api.jt.get_dair_glance_showback_usage(project_id, start_date, end_date)
            ws_s.write(0,0,_("Name"), table_header)
            ws_s.write(0,1,_("Hours"), table_header)
            ws_s.write(0,2,_("Size (GB)"), table_header)
            row=1
            if (type(usage['Snapshots'])  == type(dict())):
                for k, v in usage['Snapshots'].iteritems():
                    ws_s.write(row,0, k)
                    ws_s.write(row,1, v['hours'])
                    ws_s.write(row,2, v['size'])
                    row +=1
            ws_v = wb.add_sheet(_('Volumes'))
            first_col = ws_v.col(0)
            first_col.width = 256 * 30
            usage['Volumes'] = api.jt.get_dair_cinder_showback_usage(project_id, start_date, end_date)
            ws_v.write(0,0,_("Name"), table_header)
            ws_v.write(0,1,_("Hours"), table_header)
            ws_v.write(0,2,_("Size (GB)"), table_header)
            row=1
            if (type(usage['Volumes'])  == type(dict())):
                for k, v in usage['Volumes'].iteritems():
                    ws_v.write(row,0, k)
                    ws_v.write(row,1, v['hours'])
                    ws_v.write(row,2, v['size'])
                    row +=1
            ws_o = wb.add_sheet(_('Object Storage'))
            first_col = ws_o.col(0)
            second_col = ws_o.col(1)
            third_col = ws_o.col(2)
            first_col.width = 256 * 15
            second_col.width = 256 * 15
            third_col.width = 256 * 15
            usage['Swift'] = api.jt.get_dair_object_store_showback_usage(project_id, start_date, end_date)
            ws_o.write(0,0,_("Space usage"), table_header)
            ws_o.write(0,1,_("Container count"), table_header)
            ws_o.write(0,2,_("Object count"), table_header)
            row=1
            if (type(usage['Swift'])  == type(dict())):
                for k, v in usage['Swift'].iteritems():
                    ws_o.write(row,0, v['space_usage'])
                    ws_o.write(row,1, v['container_count'])
                    ws_o.write(row,2, v['object_count'])
                    row +=1
            response = HttpResponse(mimetype = 'application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="{0}-{1}-{2}-{3}.xls"'.format(_("summary-from"),start_date,_("to"),end_date)
            wb.save(response)
            return response

class WarningView(TemplateView):
    template_name = "project/_warning.html"
