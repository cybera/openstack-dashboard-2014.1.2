# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""
Context processors used by Horizon.
"""

from django.conf import settings


def openstack(request):
    """Context processor necessary for OpenStack Dashboard functionality.

    The following variables are added to the request context:

    ``authorized_tenants``
        A list of tenant objects which the current user has access to.

    ``regions``

        A dictionary containing information about region support, the current
        region, and available regions.
    """
    context = {}

    # Auth/Keystone context
    context.setdefault('authorized_tenants', [])
    if request.user.is_authenticated():
        # MJ - Sort tenants alphabetically
        request.user.authorized_tenants.sort(key=lambda x: x.name.lower())
        context['authorized_tenants'] = request.user.authorized_tenants

    # Region context/support
    available_regions = getattr(settings, 'AVAILABLE_REGIONS', [])
    regions = {'support': len(available_regions) > 1,
               'current': {'endpoint': request.session.get('region_endpoint'),
                           'name': request.session.get('region_name')},
               'available': [{'endpoint': region[0], 'name':region[1]} for
                             region in available_regions]}
    context['regions'] = regions

    # jt
    from openstack_dashboard.api import jt
    context['reseller_logo'] = 'logo2.png'
    context['reseller_splash'] = 'logo.png'
    fqdn = request.META.get('HTTP_HOST', 'localhost.localdomain')
    domain = ""
    try:
        domain,blah = fqdn.split('.', 1)
    except:
        domain = "localhost"
    reseller_logo = jt.get_reseller_logo(domain)
    if reseller_logo != 'Information not available.':
        context['reseller_logo'] = reseller_logo

    reseller_splash = jt.get_reseller_splash(domain)
    if reseller_splash != 'Information not available.':
        context['reseller_splash'] = reseller_splash

    dair_admin_notice = jt.get_dair_admin_notice()
    dair_admin_notice_link = jt.get_dair_admin_notice_link()
    context['dair_admin_notice'] = ""
    if dair_admin_notice != None:
        if dair_admin_notice_link != None:
            dair_admin_notice = '%s <a href="%s">More information</>.' % (dair_admin_notice, dair_admin_notice_link)
        context['dair_admin_notice'] = dair_admin_notice

    return context
