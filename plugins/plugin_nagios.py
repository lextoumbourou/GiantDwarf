import urllib2
from datetime import datetime

from BeautifulSoup import BeautifulSoup

from GiantDwarf import GiantDwarfPlugin
import settings

class Nagios(GiantDwarfPlugin):
    def __init__(self):
        super(Nagios, self).__init__()
        self.last_run = datetime.now()

    def _open_page(self):
        """Return HTML content from a webpage as a string
        Handle authentication using credentials specified in settings.py

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


    def _to_datetime(self, time_string):
        """Simple wrapper for converting Nagios dates to
        a Python datetime object

        """
        format_string = "%Y-%m-%d %H:%M:%S"
        return datetime.strptime(time_string, format_string)

    def _get_events(self, html):
        """Return latest Nagios event (based on last polling period)
        as an array of dictionaries

        """
        output = []
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
        try:
            trs = soup.find('table', 'notifications').findAll('tr')
        except AttributeError:
            # We didn't find anything, don't bother parsing it
            return output

        if not trs:
            return output

        for tr in trs[2:]:
            td = tr.findAll('td')
            host = td[0].a.text
            try:
                service = td[1].a.text
            except AttributeError:
                service = "N/A"
            level = td[2].text
            time = td[3].text
            info = td[6].text
            contact = td[4].text
            # Ignore pager notifications
            if contact.endswith('pager'):
                continue
            output.append({'host': host,
                           'service': service,
                           'level': level,
                           'time': self._to_datetime(time),
                           'info': info})
        return output


    def run(self, room):
        """Send the event information to the Campfire room
        and return the last event's time

        """
        html = self._open_page()
        if not html:
            return False

        nagios_events = self._get_events(html)
        if not nagios_events:
            return False

        for event in nagios_events:
            if event['time'] <= self.last_run:
                # Event is older then last event, skip
                continue

            # Use Alien man if no icon has been defined for the event level
            try:
                icon = settings.ALERT_ICONS[event['level']]
            except KeyError:
                icon = ':alien:'

            msg = "{0} {1} | {2} | {3} | {4}".format(icon,
                                                     event['time'],
                                                     event['service'],
                                                     event['host'],
                                                     event['info'])
            # Say what the hell is going down!
            room.speak(msg)

        # We have a new last run time
        self.last_run = nagios_events[-1]['time']
        return True
