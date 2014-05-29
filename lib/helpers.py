from datetime import datetime

import urllib2
import base64


def load_class(plugin, class_name):
    """Return a class for instantiation from a module name"""
    loaded_mod = __import__(plugin, fromlist=[plugin])
    return getattr(loaded_mod, class_name)


def get_internal(url, username=None, password=None):
    """Return HTML content from a webpage as a string"""
    password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    if username and password:
        password_manager.add_password(None, url,
                                      username,
                                      password)
    auth_handler = urllib2.HTTPBasicAuthHandler(password_manager)

    # Force it not to use a proxy for local stuff
    proxy_handler = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(auth_handler, proxy_handler)
    urllib2.install_opener(opener)
    try:
        page_handle = urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        print "Connection to internal site failed ", e
        return None
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    output = response.read()
    response.close()
    return output

def to_datetime(time_string):
    """Simple wrapper for converting Nagios dates to a Python datetime object
    """
    format_string = "%Y-%m-%d %H:%M:%S"
    return datetime.strptime(time_string, format_string)
