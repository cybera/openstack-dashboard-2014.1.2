from django.conf import settings
from django.template.defaultfilters import capfirst  # noqa
from django.template.defaultfilters import floatformat  # noqa
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView  # noqa
from django import http
from django.http import HttpResponse

from horizon.utils import csvbase
from horizon import tabs

from openstack_dashboard import api

from .tabs import DAIRUsageTabs
import requests
import csv

class DAIRUsageView(tabs.TabView):
    tab_group_class = DAIRUsageTabs
    template_name = 'project/cloudtracker_usage/index.html'

    def get(self, request, *args, **kwargs):
        return super(DAIRUsageView, self).get(request, *args, **kwargs)

class DAIRProjectData(TemplateView):
    def get(self, request, *args, **kwargs):
        from_date = self.request.GET.get('from', '7d')
        project_id = self.request.user.tenant_id
        data_format = self.request.GET.get('format', False)
        graphite_server = getattr(settings, 'DAIR_GRAPHITE_SERVER')
        base_url = 'http://%s:8180/render?from=-%s&width=800&format=%s&target=' % (graphite_server, from_date, data_format)
        query_results = {}
        queries = {
            'project_allocated_instances': "aliasSub(aliasByNode(cactiStyle(summarize(keepLastValue(projects.%s.cloud_usage-*.instances),'5min','avg')), 2), 'cloud_usage-([^\\n\\r]*)', %s )" % (project_id,'"'+_('number of instances in')+' \\1"'),
            'project_allocated_cpu': "aliasSub(aliasByNode(summarize(keepLastValue(projects.%s.cloud_usage*.cpu),'5min','avg'), 2),'cloud_usage-([^\\n\\r]*)', %s )" % (project_id, '"'+_('number of virtual cpus in')+' \\1"'),
            'project_allocated_memory': "aliasSub(aliasByNode(summarize(keepLastValue(projects.%s.cloud_usage*.memory),'5min','avg'), 2),'cloud_usage-([^\\n\\r]*)', %s)" % (project_id, '"'+_('memory usage in ')+' \\1"'),
            'project_allocated_ephemeral_disk': "aliasSub(aliasByNode(summarize(keepLastValue(projects.%s.cloud_usage*.disk),'5min','avg'), 2),'cloud_usage-([^\\n\\r]*)', %s)" % (project_id, '"'+_('disk usage in ')+' \\1"'),
        }
        query = self.request.GET.get('query', False)
        if query:
             try:
                r = requests.get("%s%s" % (base_url, queries[query]))
                r_content=r.content
             except requests.ConnectionError:
                r_content="Information not available..."
             return http.HttpResponse(r_content)

class DAIRProjectDataCSV(TemplateView):
    def get(self, request, *args, **kwargs):
        from_date = self.request.GET.get('from', '7d')
        project_id = self.request.user.tenant_id
        data_format = self.request.GET.get('format', False)
        graphite_server = getattr(settings, 'DAIR_GRAPHITE_SERVER')
        base_url = 'http://%s:8180/render?from=-%s&width=800&format=%s&target=' % (graphite_server, from_date, data_format)
        query_results = {}
        queries = {
            'project_allocated_instances': "aliasSub(aliasByNode(summarize(keepLastValue(projects.%s.cloud_usage-*.instances),'5min','avg'), 2), 'cloud_usage-([^\\n\\r]*)', 'number of instances in \\1')" % project_id,
            'project_allocated_cpu': "aliasSub(aliasByNode(summarize(keepLastValue(projects.%s.cloud_usage*.cpu),'5min','avg'), 2),'cloud_usage-([^\\n\\r]*)', 'number of virtual cpus in \\1')" % project_id,
            'project_allocated_memory': "aliasSub(aliasByNode(summarize(keepLastValue(projects.%s.cloud_usage*.memory),'5min','avg'), 2),'cloud_usage-([^\\n\\r]*)', 'memory usage in \\1')" % project_id,
            'project_allocated_ephemeral_disk': "aliasSub(aliasByNode(summarize(keepLastValue(projects.%s.cloud_usage*.disk),'5min','avg'), 2),'cloud_usage-([^\\n\\r]*)', 'disk usage in \\1')" % project_id,
        }

        query = self.request.GET.get('query', False)
        if query:
            r = requests.get("%s%s" % (base_url, queries[query]))
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(query)
            w = csv.writer(response)
            decoded_content = r.content.decode('utf-8')
            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
            my_list = list(cr)
            w.writerow([_("Name"),_("Timestamp"),_("Value")])
            for row in my_list:
                w.writerow(row)
            return response

class DAIRInstanceData(TemplateView):
    def get(self, request, *args, **kwargs):
        from_date = self.request.GET.get('from', '7d')

        instance_id = self.request.GET.get('instance', False)
        instances, foo = api.nova.server_list(self.request)
        if len([x for x in instances if x.id == instance_id]) == 0:
            return None

        data_format = self.request.GET.get('format', False)
        if data_format not in ['csv', 'json', False]:
            return None
        project_id = self.request.user.tenant_id
        graphite_server = getattr(settings, 'DAIR_GRAPHITE_SERVER')
        base_url = 'http://%s:8180/render?from=-%s&width=800&format=%s&target=' % (graphite_server, from_date, data_format)
        query_results = {}
        queries = {
            'instance_actual_cpu_time': "alias(derivative(summarize(projects.%s.instances.%s.cpu.cpu_time, '5min', 'avg')), %s)" % (project_id, instance_id,'"'+_('cpu_time')+'"'),
            'instance_actual_memory': "alias(scale(summarize(projects.%s.instances.%s.memory.available,'5min','avg'), 1024), %s )&target=alias(scale(summarize(projects.%s.instances.%s.memory.used,'5min','avg'),1024), %s)&yMin=0" % (project_id, instance_id, '"'+_('memory available ')+'"', project_id, instance_id,'"'+_('memory used ')+'"'),
            'instance_actual_network_bytes': "alias(derivative(summarize(projects.%s.instances.%s.interface.eth0.rx_bytes, '5min', 'max')), %s)&target=alias(derivative(summarize(projects.%s.instances.%s.interface.eth0.tx_bytes,'5min','max')), %s)&yMin=0" % (project_id, instance_id, '"'+_('rx_bytes (received) ')+'"', project_id, instance_id, '"'+_('tx_bytes (transmitted)')+'"'),
            'instance_actual_disk_usage': "alias(summarize(projects.%s.instances.%s.disk.vda.bytes_used,'5min','avg'), %s)&yMin=0" % (project_id, instance_id,'"'+_('bytes_used ')+'"'),
            'instance_actual_disk_io': "alias(derivative(summarize(projects.%s.instances.%s.disk.vda.wr_req,'5min','avg')), %s)&target=alias(derivative(summarize(projects.%s.instances.%s.disk.vda.rd_req,'5min','avg')), %s)&yMin=0" % (project_id, instance_id, '"'+_('wr_req (writes) ')+'"',project_id, instance_id, '"'+_('rd_req (reads)')+'"'),
        }

        query = self.request.GET.get('query', False)

        if query:
            try:
                print(queries[query])
                r = requests.get("%s%s" % (base_url,queries[query]))
                r_content=r.content
            except requests.ConnectionError:
                r_content="Information not available..."
            return http.HttpResponse(r_content)

class DAIRInstanceDataCSV(TemplateView):
    def get(self, request, *args, **kwargs):
        from_date = self.request.GET.get('from', '7d')

        instance_id = self.request.GET.get('instance', False)
        instances, foo = api.nova.server_list(self.request)
        if len([x for x in instances if x.id == instance_id]) == 0:
            return None

        data_format = self.request.GET.get('format', False)
        if data_format not in ['csv', 'json', False]:
            return None

        project_id = self.request.user.tenant_id
        graphite_server = getattr(settings, 'DAIR_GRAPHITE_SERVER')
        base_url = 'http://%s:8180/render?from=-%s&width=800&format=%s&target=' % (graphite_server, from_date, data_format)
        query_results = {}
        queries = {
            'instance_actual_cpu_time': "aliasByNode(derivative(summarize(projects.%s.instances.%s.cpu.cpu_time, '5min', 'avg')), 5)" % (project_id, instance_id),
            'instance_actual_memory': "aliasByNode(scale(summarize(projects.%s.instances.%s.memory.available,'5min','avg'), 1024), 5)&target=aliasByNode(scale(summarize(projects.%s.instances.%s.memory.used,'5min','avg'),1024),5)&yMin=0" % (project_id, instance_id, project_id, instance_id),
            'instance_actual_network_bytes': "alias(derivative(summarize(projects.%s.instances.%s.interface.eth0.rx_bytes, '5min', 'max')), 'rx_bytes (received)')&target=alias(derivative(summarize(projects.%s.instances.%s.interface.eth0.tx_bytes,'5min','max')),'tx_byes (transmitted)')&yMin=0" % (project_id, instance_id, project_id, instance_id),
            'instance_actual_disk_usage': "aliasByNode(summarize(projects.%s.instances.%s.disk.vda.bytes_used,'5min','avg'),6)&yMin=0" % (project_id, instance_id),
            'instance_actual_disk_io': "alias(derivative(summarize(projects.%s.instances.%s.disk.vda.wr_req,'5min','avg')),'wr_req (writes)')&target=alias(derivative(summarize(projects.%s.instances.%s.disk.vda.rd_req,'5min','avg')), 'rd_req (reads)')&yMin=0" % (project_id, instance_id, project_id, instance_id),
        }

        query = self.request.GET.get('query', False)
        if query:
            r = requests.get("%s%s" % (base_url, queries[query]))
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(query)
            w = csv.writer(response)
            decoded_content = r.content.decode('utf-8')
            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
            my_list = list(cr)
            w.writerow([_("Name"),_("Timestamp"),_("Value")])
            for row in my_list:
                w.writerow(row)
            return response

class DAIRInstanceDataCSVSummary(TemplateView):
    def get(self, request, *args, **kwargs):
        from_date = self.request.GET.get('from', '7d')

        instance_id = self.request.GET.get('instance', False)
        instances, foo = api.nova.server_list(self.request)
        if len([x for x in instances if x.id == instance_id]) == 0:
            return None

        data_format = self.request.GET.get('format', False)
        if data_format not in ['csv', 'json', False]:
            return None

        project_id = self.request.user.tenant_id
        graphite_server = getattr(settings, 'DAIR_GRAPHITE_SERVER')
        base_url = 'http://%s:8180/render?from=-%s&width=800&format=%s&target=' % (graphite_server, from_date, data_format)
        query_results = {}
        queries = {
            'instance_actual_cpu_time': "aliasByNode(derivative(summarize(projects.%s.instances.%s.cpu.cpu_time, '5min', 'avg')), 5)" % (project_id, instance_id),
            'instance_actual_memory': "alias(scale(summarize(projects.%s.instances.%s.memory.available,'5min','avg'), 1024),'memory available')&target=alias(scale(summarize(projects.%s.instances.%s.memory.used,'5min','avg'),1024),'memory used')&yMin=0" % (project_id, instance_id, project_id, instance_id),
            'instance_actual_network_bytes': "alias(derivative(summarize(projects.%s.instances.%s.interface.eth0.rx_bytes, '5min', 'max')), 'rx_bytes (received)')&target=alias(derivative(summarize(projects.%s.instances.%s.interface.eth0.tx_bytes,'5min','max')),'tx_byes (transmitted)')&yMin=0" % (project_id, instance_id, project_id, instance_id),
            'instance_actual_disk_usage': "aliasByNode(summarize(projects.%s.instances.%s.disk.vda.bytes_used,'5min','avg'),6)&yMin=0" % (project_id, instance_id),
            'instance_actual_disk_io': "alias(derivative(summarize(projects.%s.instances.%s.disk.vda.wr_req,'5min','avg')),'wr_req (writes)')&target=alias(derivative(summarize(projects.%s.instances.%s.disk.vda.rd_req,'5min','avg')), 'rd_req (reads)')&yMin=0" % (project_id, instance_id, project_id, instance_id),
        }
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(_('Instance_Usage_Summary'))
        w = csv.writer(response)
        try:
            r1 = requests.get("%s%s" % (base_url, queries["instance_actual_cpu_time"]))
            decoded_content = r1.content.decode('utf-8')
            cr1 = csv.reader(decoded_content.splitlines(), delimiter=',')
            my_list1 = list(cr1)
        except requests.ConnectionError:
            my_list1 = list(" ")

        try:
            r2 = requests.get("%s%s" % (base_url, queries["instance_actual_memory"]))
            decoded_content = r2.content.decode('utf-8')
            cr2 = csv.reader(decoded_content.splitlines(), delimiter=',')
            my_list2 = list(cr2)
        except requests.ConnectionError:
            my_list2 = list(" ")
        my_list2_1 = my_list2[:len(my_list2)/2]
        my_list2_2 = my_list2[len(my_list2)/2:]

        try:
            r3 = requests.get("%s%s" % (base_url, queries["instance_actual_network_bytes"]))
            decoded_content = r3.content.decode('utf-8')
            cr3 = csv.reader(decoded_content.splitlines(), delimiter=',')
            my_list3 = list(cr3)
        except requests.ConnectionError:
            my_list3 = list(" ")
        my_list3_1 = my_list3[:len(my_list3)/2]
        my_list3_2 = my_list3[len(my_list3)/2:]

        try:
            r4 = requests.get("%s%s" % (base_url, queries["instance_actual_disk_usage"]))
            decoded_content = r4.content.decode('utf-8')
            cr4 = csv.reader(decoded_content.splitlines(), delimiter=',')
            my_list4 = list(cr4)
        except requests.ConnectionError:
            my_list4 = list(" ")

        try:
            r5 = requests.get("%s%s" % (base_url, queries["instance_actual_disk_io"]))
            decoded_content = r5.content.decode('utf-8')
            cr5 = csv.reader(decoded_content.splitlines(), delimiter=',')
            my_list5 = list(cr5)
        except requests.ConnectionError:
            my_list5 = list(" ")
        my_list5_1 = my_list5[:len(my_list5)/2]
        my_list5_2 = my_list5[len(my_list5)/2:]

        w.writerow([_("timestamp"), _("cpu_time"), (_("memory available")).encode('utf-8'), (_("memory used")).encode('utf-8'), (_("rx_bytes (received)")).encode('utf-8'), _("tx_byes (transmitted)"), (_("bytes_used")).encode('utf-8'), (_("wr_req (writes)")).encode('utf-8'), _("rd_req (reads)")])

        for row1, row2_1, row2_2, row3_1, row3_2, row4, row5_1, row5_2 in zip(my_list1, my_list2_1, my_list2_2, my_list3_1, my_list3_2, my_list4, my_list5_1, my_list5_2):
            w.writerow((row1[1],row1[2],row2_1[2],row2_2[2],row3_1[2],row3_2[2],row4[2],row5_1[2],row5_2[2]))
        return response

class DAIRProjectDataCSVSummary(TemplateView):
    def get(self, request, *args, **kwargs):
        from_date = self.request.GET.get('from', '7d')
        project_id = self.request.user.tenant_id
        data_format = self.request.GET.get('format', False)
        graphite_server = getattr(settings, 'DAIR_GRAPHITE_SERVER')
        base_url = 'http://%s:8180/render?from=-%s&width=800&format=%s&target=' % (graphite_server, from_date, data_format)
        query_results = {}
        queries = {
            'project_allocated_instances': "aliasSub(aliasByNode(summarize(keepLastValue(projects.%s.cloud_usage-*.instances),'5min','avg'), 2), 'cloud_usage-([^\\n\\r]*)', 'number of instances in \\1')" % project_id,
            'project_allocated_cpu': "aliasSub(aliasByNode(summarize(keepLastValue(projects.%s.cloud_usage*.cpu),'5min','avg'), 2),'cloud_usage-([^\\n\\r]*)', 'number of virtual cpus in \\1')" % project_id,
            'project_allocated_memory': "aliasSub(aliasByNode(summarize(keepLastValue(projects.%s.cloud_usage*.memory),'5min','avg'), 2),'cloud_usage-([^\\n\\r]*)', 'memory usage in \\1')" % project_id,
            'project_allocated_ephemeral_disk': "aliasSub(aliasByNode(summarize(keepLastValue(projects.%s.cloud_usage*.disk),'5min','avg'), 2),'cloud_usage-([^\\n\\r]*)', 'disk usage in \\1')" % project_id,
        }
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(_('Project_Usage_Summary'))
        w = csv.writer(response)

        try:
            r1 = requests.get("%s%s" % (base_url, queries["project_allocated_instances"]))
            decoded_content = r1.content.decode('utf-8')
            cr1 = csv.reader(decoded_content.splitlines(), delimiter=',')
            my_list1 = list(cr1)
        except requests.ConnectionError:
            my_list1 = list(" ")
        my_list1_1 = my_list1[:len(my_list1)/2]
        my_list1_2 = my_list1[len(my_list1)/2:]

        try:
            r2 = requests.get("%s%s" % (base_url, queries["project_allocated_cpu"]))
            decoded_content = r2.content.decode('utf-8')
            cr2 = csv.reader(decoded_content.splitlines(), delimiter=',')
            my_list2 = list(cr2)
        except requests.ConnectionError:
            my_list2 = list(" ")
        my_list2_1 = my_list2[:len(my_list2)/2]
        my_list2_2 = my_list2[len(my_list2)/2:]

        try:
            r3 = requests.get("%s%s" % (base_url, queries["project_allocated_memory"]))
            decoded_content = r3.content.decode('utf-8')
            cr3 = csv.reader(decoded_content.splitlines(), delimiter=',')
            my_list3 = list(cr3)
        except requests.ConnectionError:
            my_list3 = list(" ")
        my_list3_1 = my_list3[:len(my_list3)/2]
        my_list3_2 = my_list3[len(my_list3)/2:]

        try:
            r4 = requests.get("%s%s" % (base_url, queries["project_allocated_ephemeral_disk"]))
            decoded_content = r4.content.decode('utf-8')
            cr4 = csv.reader(decoded_content.splitlines(), delimiter=',')
            my_list4 = list(cr4)
        except requests.ConnectionError:
            my_list4 = list(" ")
        my_list4_1 = my_list4[:len(my_list4)/2]
        my_list4_2 = my_list4[len(my_list4)/2:]


        w.writerow([_("timestamp"),_("number of instances in")+" alberta",_("number of instances in")+" quebec",_("number of virtual cpus in")+" alberta",_("number of virtual cpus in")+" quebec",(_("memory usage in")).encode('utf-8')+" alberta",(_("memory usage in")).encode('utf-8')+" quebec",(_("disk usage in")).encode('utf-8')+" alberta",(_("disk usage in")).encode('utf-8') +" quebec"])

        for row1_1, row1_2, row2_1, row2_2, row3_1, row3_2, row4_1, row4_2 in zip(my_list1_1, my_list1_2, my_list2_1, my_list2_2, my_list3_1, my_list3_2, my_list4_1, my_list4_2):
            w.writerow((row1_1[1],row1_1[2],row1_2[2],row2_1[2],row2_2[2],row3_1[2],row3_2[2],row4_1[2],row4_2[2]))
        return response

class WarningView(TemplateView):
    template_name = "project/_warning.html"
