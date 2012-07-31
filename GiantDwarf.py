from pyfire import Campfire
from BeautifulSoup import BeautifulSoup
from sys import exit
from time import sleep
from datetime import datetime
from lib import utils
import settings

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
                       'time'   : utils.to_datetime(time),
                       'info'   : info})
    return output

def send_to_room(last_run, room):
    """
    Sends the event information to the Campfire room
    and return the last event's time
    """
    html = utils.open_page()
    if not html:
        return last_run

    nagios_events = get_nagios_events(html)
    if not nagios_events:
        return last_run

    for event in nagios_events:
        if event['time'] <= last_run:
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
    return nagios_events[-1]['time']
        
if __name__ == '__main__':
    # Setup Campfire and join our room
    c = Campfire(settings.SUBDOMAIN, settings.TOKEN, 'x', ssl=settings.USE_SSL)
    room = c.get_room_by_name(settings.ROOM)
    room.join()

    # Ensure we don't get old Nagios events
    last_run = datetime.now()
    print "Online and ready"

    while True:
        try:
            last_run = send_to_room(last_run, room)
            print "Last run time ", last_run
            sleep(settings.FETCH_INTERVAL)
        except KeyboardInterrupt:
            print "Okay, I'm leaving the room now"
            room.leave()
            exit()
