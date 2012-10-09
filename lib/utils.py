import urllib2
import settings
from datetime import datetime


def open_page():
    """
    Return HTML content from a webpage as a string
    Handles authentication using credentials specified in settings.py
    """
    nagios_url = settings.NAGIOS_DOMAIN
    nagios_url += '/cgi-bin/nagios3/notifications.cgi'
    nagios_url += '?contact=all&archive=0&type=0&oldestfirst=on'
    password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, nagios_url,
                                  settings.NAGIOS_USERNAME,
                                  settings.NAGIOS_PASSWORD)
    auth_handler = urllib2.HTTPBasicAuthHandler(password_manager)
    # Force it not to use a proxy
    proxy_handler = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(auth_handler, proxy_handler)
    urllib2.install_opener(opener)
    try:
        page_handle = urllib2.urlopen(nagios_url)
    except HTTPError, e:
        print "Connection to internal site failed ", e
        return None
    req = urllib2.Request(nagios_url)
    response = urllib2.urlopen(req)
    output = response.read()
    response.close()
    return output


def to_datetime(time_string):
    """
    Simple wrapper for converting Nagios dates to
    a Python datetime object
    """
    format_string = "%Y-%m-%d %H:%M:%S"
    return datetime.strptime(time_string, format_string)
