#####################################################
# General config parameters
#####################################################
TOKEN     = ''
SUBDOMAIN = ''
ROOM      = ''
USE_SSL   = True

# Logging
LOG_FILE = '/var/log/giantdwarf.log'

######################################################
# Plugins
######################################################

# Passive plugins are called periodically and can only send data to the room.
# Should be a list of tuples in format: ('module.name', 'ClassName')
PASSIVE_PLUGINS = [
    ('plugins.nagios', 'Nagios'),
]

# Active plugins are called with commands from the room
# Should be a list of tuples in format: ('module.name', 'ClassName')
ACTIVE_PLUGINS = [
    ('plugins.jenkins', 'Jenkins'),
    ('plugins.say', 'Say'),
]

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
