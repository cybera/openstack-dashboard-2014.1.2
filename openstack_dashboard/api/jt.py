from dateutil import parser
from django.conf import settings
from horizon import conf
import MySQLdb
from django import http

import glance
import requests
import datetime

def _dbconnect(db=None):
    username = getattr(settings, 'DAIR_MYSQL_USERNAME')
    password = getattr(settings, 'DAIR_MYSQL_PASSWORD')
    host = getattr(settings, 'DAIR_MYSQL_HOST')
    if db == None:
        db = 'dair_information'
    return MySQLdb.connect(host=host,user=username,passwd=password,db=db)

def get_image_quota(project_id):
    import subprocess
    cmd = 'sudo /root/novac/bin/novac quota-image-get %s' % project_id
    image_limit = subprocess.check_output(cmd, shell=True)
    return int(image_limit.strip())

def set_image_quota(project_id, quota):
    import subprocess
    cmd = 'sudo /root/novac/bin/novac quota-image-set %s %s' % (project_id, quota)
    subprocess.check_call(cmd, shell=True)

def get_image_count(project_id, request):
    (all_images, more_images) = glance.image_list_detailed(request)
    images = [im for im in all_images if im.owner == project_id]
    return len(images)

def get_object_mb_quota(project_id):
    import subprocess
    cmd = 'sudo /root/novac/bin/novac quota-object_mb-get %s' % project_id
    object_mb = subprocess.check_output(cmd, shell=True)
    return int(object_mb.strip())

def set_object_mb_quota(project_id, quota):
    import subprocess
    cmd = 'sudo /root/novac/bin/novac quota-object_mb-set %s %s' % (project_id, quota)
    subprocess.check_call(cmd, shell=True)

def get_object_mb_usage(project_id):
    import subprocess
    cmd = 'sudo /root/novac/bin/novac quota-object_mb-usage %s' % project_id
    object_mb_usage = subprocess.check_output(cmd, shell=True)
    return int(object_mb_usage.strip())

def get_expiration_date(project_id):
    try:
        db = _dbconnect()
        c = db.cursor()
        query = "SELECT date_format(expiration_date, '%%M %%d, %%Y') from project_information where project_id = %s"
        data = (project_id)
        c.execute(query, data)
        date = c.fetchone()
        if date is not None:
            return date[0]
        return "Information not available."
    except MySQLdb.Error, e:
        print(str(e))
        return "Information not available..."

def set_expiration_date(project_id, expiration_date):
    try:
        db = _dbconnect()
        c = db.cursor()
        expiration_date = parser.parse(expiration_date)
        query = "INSERT INTO project_information (project_id, expiration_date) VALUES (%s, %s) ON DUPLICATE KEY UPDATE expiration_date = %s"
        data = (project_id, expiration_date, expiration_date)
        c.execute(query, data)
        db.commit()
    except Exception as e:
        print(str(e))

def get_start_date(project_id):
    try:
        db = _dbconnect()
        c = db.cursor()
        query = "SELECT date_format(start_date, '%%M %%d, %%Y') from project_information where project_id = %s"
        data = (project_id)
        c.execute(query, data)
        date = c.fetchone()
        if date is not None:
            return date[0]
        return "Information not available."
    except MySQLdb.Error, e:
        print(str(e))
        return "Information not available..."

def set_start_date(project_id, start_date):
    try:
        db = _dbconnect()
        c = db.cursor()
        start_date = parser.parse(start_date)
        query = "INSERT INTO project_information (project_id, start_date) VALUES (%s, %s) ON DUPLICATE KEY UPDATE start_date = %s"
        data = (project_id, start_date, start_date)
        c.execute(query, data)
        db.commit()
    except Exception as e:
        print(str(e))

def get_dair_notice(project_id):
    try:
        db = _dbconnect()
        c = db.cursor()
        query = "SELECT notice from project_information where project_id = %s"
        data = (project_id)
        c.execute(query, data)
        notice = c.fetchone()
        if notice is not None:
            return notice[0]
        return ""
    except MySQLdb.Error, e:
        print(str(e))
        return "Information not available..."

def set_dair_notice(project_id, notice, is_admin_notice):
    try:
        if is_admin_notice:
            project_id = 'admin'
        db = _dbconnect()
        c = db.cursor()
        query = "INSERT INTO project_information (project_id, notice) VALUES (%s, %s) ON DUPLICATE KEY UPDATE notice = %s"
        data = (project_id, notice, notice)
        c.execute(query, data)
        db.commit()
    except Exception as e:
        print(str(e))

def get_dair_notice_link(project_id):
    try:
        db = _dbconnect()
        c = db.cursor()
        query = "SELECT notice_link from project_information where project_id = %s"
        data = (project_id)
        c.execute(query, data)
        notice_link = c.fetchone()
        if notice_link is not None:
            return notice_link[0]
        return ""
    except MySQLdb.Error, e:
        print(str(e))
        return "Information not available..."

def set_dair_notice_link(project_id, link, is_admin_notice):
    try:
        if is_admin_notice:
            project_id = 'admin'
        db = _dbconnect()
        c = db.cursor()
        query = "INSERT INTO project_information (project_id, notice_link) VALUES (%s, %s) ON DUPLICATE KEY UPDATE notice_link = %s"
        data = (project_id, link, link)
        c.execute(query, data)
        db.commit()
    except Exception as e:
        print(str(e))

def get_dair_admin_notice():
    try:
        db = _dbconnect()
        c = db.cursor()
        query = "SELECT notice from project_information where project_id = 'admin'"
        c.execute(query)
        notice = c.fetchone()
        if notice is not None:
            return notice[0]
        return None
    except MySQLdb.Error, e:
        print(str(e))
        return "Information not available..."

def get_dair_admin_notice_link():
    try:
        db = _dbconnect()
        c = db.cursor()
        query = "SELECT notice_link from project_information where project_id = 'admin'"
        c.execute(query)
        notice_link = c.fetchone()
        if notice_link is not None and notice_link[0] != "":
            return notice_link[0]
        return None
    except MySQLdb.Error, e:
        print(str(e))
        return "Information not available..."

def get_reseller_logos():
    #logos = {}
    #with open('/etc/openstack-dashboard/dair-reseller-logos.txt') as f:
    #    for line in f:
    #        line = line.strip()
    #        if line != "":
    #            foo = line.split(':')
    #            logos[foo[0]] = foo[1]
    #return logos
    return

def get_reseller_logo(domain):
    #import os.path
    #if domain not in ['nova-ab', 'nova-qc', 'nova-hl', 'nova-mi']:
    #    if os.path.isfile('/usr/share/openstack-dashboard/openstack_dashboard/static/dashboard/img/%s.png' % domain):
    #        return '%s.png' % domain
    #    return "Information not available."
    return "Information not available."

def set_reseller_logo(project_id, logo):
    #logos = get_reseller_logos()
    #logos[project_id] = logo
    #with open('/etc/openstack-dashboard/dair-reseller-logos.txt', 'w') as f:
    #    for k, v in logos.iteritems():
    #        f.write("%s:%s\n" % (k,v))
    return

def get_reseller_splash(domain):
    #import os.path
    #if domain not in ['nova-ab', 'nova-qc', 'nova-hl', 'nova-mi']:
    #    if os.path.isfile('/usr/share/openstack-dashboard/openstack_dashboard/static/dashboard/img/%s-splash.png' % domain):
    #        return '%s-splash.png' % domain
    #    return "Information not available."
    return "Information not available."

def get_used_resources(project_id):
    import subprocess
    resources = {}
    cmd = 'sudo /root/novac/bin/novac quota-get-used-resources %s' % project_id
    x = subprocess.check_output(cmd, shell=True)
    for r in x.split("\n"):
        r = r.strip()
        if r:
            (resource, used) = r.split(' ')
            resources[resource] = used
    return resources
def get_dair_bandwidth_showback_usage(tenant, start, end):
    usage = {}
    try:
        start_date = parser.parse(start)
        start_date=str(start_date)
        start_date1 = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        start_date1 = start_date1.strftime('%H:%M%Y%m%d')
        end_date = parser.parse(end)
        end_date=str(end_date)
        end_date1 = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
        end_date1 = end_date1.strftime('%H:%M%Y%m%d')
        graphite = getattr(settings, 'DAIR_GRAPHITE_SERVER')
        query_bytes_received = "target=integral(nonNegativeDerivative(sumSeries(keepLastValue(projects.%s.*.network.total_bytes_received))))&from=%s&until=%s" % (tenant, start_date1, end_date1)
        query_bytes_transmitted = "target=integral(nonNegativeDerivative(sumSeries(keepLastValue(projects.%s.*.network.total_bytes_transmitted))))&from=%s&until=%s" % (tenant, start_date1, end_date1)
        bytes_received = requests.get ('http://'+graphite+':8180/render?'+query_bytes_received+'&format=json')
        bytes_transmitted = requests.get ('http://'+graphite+':8180/render?'+query_bytes_transmitted+'&format=json')
        usage[tenant] = {}
        usage[tenant]['bytes_received'] = '%.2f' % round((bytes_received.json()[0][u'datapoints'][-1][0] /1024 /1024),2)
        usage[tenant]['bytes_transmitted']= '%.2f' % round((bytes_transmitted.json()[0][u'datapoints'][-1][0] /1024 /1024),2)
    except Exception as e:
        print(str(e))
        return "Information not available..."
    return usage

def get_dair_object_store_showback_usage(tenant, start, end):
    usage = {}
    try:
        graphite = getattr(settings, 'DAIR_GRAPHITE_SERVER')

        query_container_count = "target=sumSeries(keepLastValue(projects.%s.*.swift.container_count,100))" % (tenant)
        query_space_usage = "target=sumSeries(keepLastValue(projects.%s.*.swift.space_usage,100))" % (tenant)
        query_object_count = "target=sumSeries(keepLastValue(projects.%s.*.swift.object_count,100))" % (tenant)

        container_count = requests.get ('http://'+graphite+':8180/render?'+query_container_count+'&format=json')
        space_usage = requests.get ('http://'+graphite+':8180/render?'+query_space_usage+'&format=json')
        object_count = requests.get ('http://'+graphite+':8180/render?'+query_object_count+'&format=json')

        usage[tenant] = {}
        usage[tenant]['container_count'] = int(container_count.json()[0][u'datapoints'][-1][0])
        usage[tenant]['object_count'] = int(object_count.json()[0][u'datapoints'][-1][0])
        usage[tenant]['space_usage']= '%.2f' % round((space_usage.json()[0][u'datapoints'][-1][0] /1024 /1024),2)
    except Exception as e:
        print(str(e))
        return "Information not available..."
    return usage

def get_dair_nova_showback_usage(tenant, start, end):
    usage = {}
    try:
    #    prices = getattr(settings, 'DAIR_SHOWBACK_PRICES')
    #    total_cost = 0
        start_date = parser.parse(start)
        end_date = parser.parse(end)
        db = _dbconnect('nova')
        c = db.cursor()
        query = "SELECT i.created_at, i.deleted_at, it.name FROM instances AS i LEFT JOIN instance_types AS it ON i.instance_type_id=it.id WHERE i.project_id = %s AND i.created_at < %s AND (i.deleted_at > %s OR i.deleted_at IS NULL)"
        data = (tenant, end_date, start_date)
        c.execute(query, data)
        rows = c.fetchall()
        for row in rows:
            start_date = row[0]
            flavor_name = row[2]
            if row[1]:
                end_date = row[1]
            hours = abs(int((end_date - start_date).total_seconds() / 60 / 60))
        #tm
        #    if flavor_name in prices['nova']:
        #        flavor_cost = prices['nova'][flavor_name]
        #    else:
        #        flavor_cost = 0
            if flavor_name in usage:
                usage[flavor_name]['count'] += 1
                usage[flavor_name]['hours'] += hours
         #       usage[flavor_name]['cost'] += float("%.2f" % (flavor_cost * hours))
         #       total_cost += float("%.2f" % (flavor_cost * hours))
            else:
                usage[flavor_name] = {}
                usage[flavor_name]['count'] = 1
                usage[flavor_name]['hours'] = hours
          #      usage[flavor_name]['cost'] = float("%.2f" % (flavor_cost * hours))
          #      total_cost += usage[flavor_name]['cost']
       # usage['total_cost'] = total_cost
    except MySQLdb.Error, e:
        print(str(e))
        return "Information not available..."
    return usage

def get_dair_glance_showback_usage(tenant, start, end):
    usage = {}
    try:
       # prices = getattr(settings, 'DAIR_SHOWBACK_PRICES')
       # total_cost = 0
        start_date = parser.parse(start)
        end_date = parser.parse(end)
        db = _dbconnect('glance')
        c = db.cursor()
        query = "SELECT created_at, deleted_at, name, size FROM images WHERE owner = %s AND created_at < %s AND (deleted_at > %s OR deleted_at IS NULL) AND status != 'killed'"
        data = (tenant, end_date, start_date)
        c.execute(query, data)
        rows = c.fetchall()
        for row in rows:
            start_date = row[0]
            name = row[2]
            if row[1]:
                end_date = row[1]
            hours = int((end_date - start_date).total_seconds() / 60 / 60)
            usage[name] = {}
            usage[name]['hours'] = hours
            usage[name]['size'] = row[3] / 1024 / 1024 / 1024.0
        #    usage[name]['cost'] = float("%.2f" % (usage[name]['size'] * hours * prices['glance']))
        #    total_cost += usage[name]['cost']
        #usage['total_cost'] = total_cost
    except MySQLdb.Error, e:
        print(str(e))
        return "Information not available..."
    return usage

def get_dair_cinder_showback_usage(tenant, start, end):
    usage = {}
    try:
        #prices = getattr(settings, 'DAIR_SHOWBACK_PRICES')
        #total_cost = 0
        start_date = parser.parse(start)
        end_date = parser.parse(end)
        db = _dbconnect('cinder')
        c = db.cursor()
        query = "SELECT created_at, deleted_at, display_name, size FROM volumes WHERE project_id = %s AND created_at < %s AND (deleted_at > %s OR deleted_at IS NULL)"
        data = (tenant, end_date, start_date)
        c.execute(query, data)
        rows = c.fetchall()
        for row in rows:
            start_date = row[0]
            name = row[2]
            if row[1]:
                end_date = row[1]
            hours = int((end_date - start_date).total_seconds() / 60 / 60)
            usage[name] = {}
            usage[name]['hours'] = hours
            usage[name]['size'] = row[3]
         #   usage[name]['cost'] = float("%.2f" % (usage[name]['size'] * hours * prices['cinder']))
         #   total_cost += usage[name]['cost']
       # usage['total_cost'] = total_cost
    except MySQLdb.Error, e:
        print(str(e))
        return "Information not available..."
    return usage
