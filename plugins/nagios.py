from datetime import datetime

from requests.auth import HTTPBasicAuth
from BeautifulSoup import BeautifulSoup


class Nagios():
    def create(self):
        self.last_run = datetime.now()
        self.nagios_url = config.get(url) + (
            '/cgi-bin/nagios3/notifications.cgi'
            '?contact=all&archive=0&type=0&oldestfirst=on'
        )

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

            if contact.endswith('pager'):
                continue

            output.append({
                'host': host, 'service': service,
                'level': level, 'time': self._to_datetime(time),
                'info': info
            })

        return output

    def run(self):
        """Send the event information to the Campfire room
        and return the last event's time
        """
        for instance in self.config['instances']:
            html = request.get(
                url=self.nagios_url, 
                auth=HTTPBasicAuth(instance['username'], instance['password'])
            )

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
                    icon = ALERT_ICONS[event['level']]
                except KeyError:
                    icon = ':alien:'

                msg = "{} | {} ({}) | {} | {} | {}".format(
                    icon, instance['name'], event['time'],
                     event['service'], event['host'], event['info']
                 )

                room = 'general'
                if 'room' in instance:
                    room = instance['room']
                elif 'room' in self.config:
                    room = self.config['room']

                self.conn.chat.post_message(
                    room, msg, username='GiantDwarf',
                    icon_url=(
                        'https://s3-us-west-2.amazonaws.com/'
                        'slack-files2/bot_icons/2014-05-28/2359113583_48.png'
                    ) 
                )

        # We have a new last run time
        self.last_run = nagios_events[-1]['time']
        return True
