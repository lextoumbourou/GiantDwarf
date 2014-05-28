from mock import MagicMock
from giantdwarf import SlackGiantDwarf


class TestSlackNagios(object):
    def setup(self):
        self.config = {
            'subdomain': 'anything',
            'token': 'ABC',
            'use_ssl': True,
            'log_file': '/tmp/slack.log',
            'log_mode': 'normal'
        }

    def test_get_connection_to_slack(self):
        slacker_mock = MagicMock()
        slack_gd = SlackGiantDwarf(self.config, slacker_mock)
        assert slack_gd.config['subdomain'] == config['subdomain']

    def test_can_load_plugin(self):
        self.config['plugins'] = [
            'nagios': 'plugins.nagios'
        ]
        slacker_mock = MagicMock()
        slack_gd = SlackGiantDwarf(self.config, slacker_mock)
        slack.gd._load_plugins()
        assert slack_gd.plugins[0]['name'] == 'nagios'
