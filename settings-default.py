#####################################################
# General config parameters
#####################################################
TOKEN = ''
SUBDOMAIN = ''  # Don't include .campfirenow.com
ROOM = ''
USE_SSL = True

# Logging
LOG_FILE = '/var/log/giantdwarf.log'

#####################################################
# Plugin specific parameters
#####################################################
ALERT_ICONS = {'CRITICAL': ':scream:',
               'WARNING': ':cold_sweat:',
               'OK': ':smiley:',
               'HOST DOWN': ':finnadie:',
               'HOST UP': ':godmode:', }

# How often should the bot perform checks
FETCH_INTERVAL = 20

# Nagios specific
NAGIOS_DOMAIN = 'http://WhereNagiosIs.com'  # don't include /nagios
                                            # unless it's non standard
NAGIOS_USERNAME = ''
NAGIOS_PASSWORD = ''
