import httplib2
import settings
from datetime import datetime

def open_page():
    """
    Return HTML content from a webpage as a string
    """
    #h = httplib2.Http(".cache")
    #h.add_credentials(settings.NAGIOS_USERNAME, settings.NAGIOS_PASSWORD)
    #resp, content = h.request(settings.NAGIOS_DOMAIN+'cgi-bin/nagios3/notifications.cgi?contact=all')
    ## Only return content if we actually found something
    #if resp['status'] == '200':
    #    return content
    #return None
    return open("/tmp/index.html").read()

def to_datetime(time_string):
    """
    Simple wrapper for converting Nagios dates to
    a Python datetime object
    """
    format_string = "%Y-%m-%d %H:%M:%S"
    return datetime.strptime(time_string, format_string)




