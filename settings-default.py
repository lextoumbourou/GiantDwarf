#####################################################
# General config parameters
#####################################################
TOKEN     = ''
SUBDOMAIN = '' # Don't include .campfirenow.com
ROOM      = '' 
USE_SSL   = True

#####################################################
# Plugin specific parameters
#####################################################
ALERT_ICONS = {'CRITICAL' :':scream:',
               'WARNING'  :':cold_sweat:',
               'OK'       :':smiley:',
               'HOST DOWN':':finnadie:',
               'HOST UP'  :':godmode:',}

# How often should the bot perform checks 
FETCH_INTERVAL = 20

# Nagios specific
NAGIOS_DOMAIN   = 'WhereNagiosIs.com' # don't include http:// or /nagios unless it's non standard
NAGIOS_USERNAME = ''
NAGIOS_PASSWORD = ''
