from django.conf.urls import patterns  # noqa
from django.conf.urls import url  # noqa

from openstack_dashboard.dashboards.project.dair_showback import views


urlpatterns = patterns('openstack_dashboard.dashboards.project.dair_showback.views',
    url(r'^$', views.DAIRShowbackView.as_view(), name='index'),
    url(r'^index$', views.DAIRShowbackView.as_view(), name='index'),
    url(r'^csv$', views.DAIRShowbackCSVView.as_view(), name='csv'),
    url(r'^warning$', views.WarningView.as_view(), name='warning'),
)
