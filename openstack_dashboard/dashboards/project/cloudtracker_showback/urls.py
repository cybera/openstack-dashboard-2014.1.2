from django.conf.urls import patterns  # noqa
from django.conf.urls import url  # noqa

from openstack_dashboard.dashboards.project.cloudtracker_showback import views


urlpatterns = patterns('openstack_dashboard.dashboards.project.cloudtracker_showback.views',
    url(r'^$', views.DAIRShowbackView.as_view(), name='index'),
    url(r'^index$', views.DAIRShowbackView.as_view(), name='index'),
    url(r'^csv_instances$', views.DAIRShowbackCSV_instancesView.as_view(), name='csv'),
    url(r'^csv_bandwidth$', views.DAIRShowbackCSV_bandwidthView.as_view(), name='csv'),
    url(r'^csv_swift$', views.DAIRShowbackCSV_swiftView.as_view(), name='csv'),
    url(r'^csv_volumes$', views.DAIRShowbackCSV_volumesView.as_view(), name='csv'),
    url(r'^csv_snapshots$', views.DAIRShowbackCSV_snapshotsView.as_view(), name='csv'),
    url(r'^csv_summary$', views.DAIRShowbackCSV_SummaryView.as_view(), name='csv'),
    url(r'^xml_summary$', views.DAIRShowbackXML_SummaryView.as_view(), name='xml'),
    url(r'^warning$', views.WarningView.as_view(), name='warning'),
)
