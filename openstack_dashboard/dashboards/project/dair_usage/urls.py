from django.conf.urls import patterns  # noqa
from django.conf.urls import url  # noqa

from openstack_dashboard.dashboards.project.dair_usage import views


urlpatterns = patterns('openstack_dashboard.dashboards.project.dair_usage.views',
    url(r'^$', views.DAIRUsageView.as_view(), name='index'),
    url(r'^index$', views.DAIRUsageView.as_view(), name='index'),
    url(r'^project_data$', views.DAIRProjectData.as_view(), name='project_data'),
    url(r'^instance_data$', views.DAIRInstanceData.as_view(), name='instance_data'),
    url(r'^warning$', views.WarningView.as_view(), name='warning'),
)
