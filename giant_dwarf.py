from pinder import Campfire
from datetime import datetime
from BeautifulSoup import BeautifulSoup
from sys import exit
from time import sleep
import settings

def open_page():
    """
    Return HTML content from a webpage as a string
    """
    h = httplib2.Http(".cache")
    h.add_credentials(settings.NAGIOS_USER, settings.NAGIOS_PASS)
    resp, content = h.request(settings.NAGIOS_DOMAIN+'cgi-bin/nagios3/notifications.cgi?contact=all')
    # Only return content if we actually found something
    if resp['status'] == '200':
        return content
    return None

def get_nagios_events(html):
    """
    Return latest Nagios event (based on last polling period)
    as an array of dictionaries
    """
    output = []
    soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
    trs = soup.find('table', 'notifications').findAll('tr')
    if not trs:
        # We didn't find anything, don't bother parsing it
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
        output.append({'host'   : host,
                       'service': service,
                       'level'  : level,
                       'time'   : to_datetime(time),
                       'info'   : info})
    return output

def to_datetime(time_string):
    """
    Simple wrapper for converting Nagios dates to
    a Python datetime object
    """
    format_string = "%Y-%m-%d %H:%M:%S"
    return datetime.strptime(time_string, format_string)

def main(room):
    """
    Main program logic
    """
    # Ensure we don't get old Nagios events
    last_run = datetime.now()

    # Program loop begins
    while True:
        html = open_page()

        if html:
            nagios_events = get_nagios_events(html)
        else:
            continue

        for event in nagios_events:
            # Check if top event is the most recent
            if event['time'] <= last_run:
                continue

            # Set the icon, if we haven't defined it in settings
            # then we get the alien man :)
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
        last_run = nagios_events[-1]['time']
        #print last_run

        # Rest!
        sleep(settings.FETCH_INTERVAL)

if __name__ == '__main__':
    # Setup Campfire and join our room
    c = Campfire(settings.SUBDOMAIN, settings.TOKEN)
    room = c.find_room_by_name(settings.ROOM)
    room.join()
    print "Online and ready."

    try:
        main(room)
    except KeyboardInterrupt:
        print "Okay, I'm leaving the room now"
        room.leave()
        exit()
