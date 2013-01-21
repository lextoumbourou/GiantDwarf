import urllib2
import base64

def open_page(url, username=None, password=None):
    """
    Return HTML content from a webpage as a string
    Handle authentication using credentials specified in settings.py

    """
    
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
