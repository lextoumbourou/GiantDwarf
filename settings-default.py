#####################################################
# General config parameters
#####################################################
TOKEN     = ''
SUBDOMAIN = ''
ROOM      = ''
USE_SSL   = True

# Logging
LOG_FILE = '/var/log/giantdwarf.log'

#####################################################
# Plugin specific parameters
#####################################################
ALERT_ICONS = {'CRITICAL' :':scream:',
               'WARNING'  :':cold_sweat:',
               'OK'       :':smiley:',
               'HOST DOWN':':finnadie:',
               'HOST UP'  :':godmode:',}

# How often should the bot perform checks
FETCH_INTERVAL = 30

# Nagios specific
NAGIOS_DOMAIN   = ''
NAGIOS_USERNAME = ''
NAGIOS_PASSWORD = ''

# Jenkins specific
JENKINS_DOMAIN = ''
JENKINS_USER = ''
JENKINS_PASSWORD = ''
JENKINS_API_TOKEN = ''
