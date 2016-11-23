from dateutil import parser
from django.conf import settings
from horizon import conf
import MySQLdb

import glance

def _dbconnect():
    username = getattr(settings, 'DAIR_MYSQL_USERNAME')
    password = getattr(settings, 'DAIR_MYSQL_PASSWORD')
    host = getattr(settings, 'DAIR_MYSQL_HOST')
    return MySQLdb.connect(host=host,user=username,passwd=password,db='dair_information')

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
