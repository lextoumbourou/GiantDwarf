import subprocess
import json

from GiantDwarf.GiantDwarf import GiantDwarfPlugin
from GiantDwarf.lib import utils

class Jenkins(GiantDwarfPlugin):
    def create(self):
        self.jenkins_url = self.config.get('Jenkins', 'jenkins_domain') 

    def _list_jobs_like(self, search=''):
        output = "" 
        url = self.jenkins_url + "/api/json"
        raw_data = utils.open_page(url)
        data = json.loads(raw_data)
        for job in data['jobs']:
            if search in job['name']:
                output += "{0} -- Status: {1}\n".format(job['name'], job['color'])

        return [output]

    def _get_last_build(self, job):
        output = ""
        url = self.jenkins_url + "/job/" + job + "/api/json/"
        raw_data = utils.open_page(url)
        if not raw_data:
            return "Couldn't find that job"

        data = json.loads(raw_data)
        last_build = data['lastBuild']['number']
        url = self.jenkins_url + "/job/{0}/{1}/api/json/".format(job, 
                                                                 last_build)
        raw_data = utils.open_page(url)
        data = json.loads(raw_data)
        if data:
            change_set = data['changeSet']['items']
            try:
                output += "Author: {0}\n".format(change_set[0]["author"]["fullName"])
            except IndexError, KeyError:
                pass

            try:
                output += "Result: {0}\n".format(data['result'])
            except IndexError, KeyError:
                pass

            try:
                output += "Msg: {0}\n".format(change_set[0]["msg"])
            except IndexError, KeyError:
                pass

            try:
                output += "Commit: {0}\n".format(change_set[0]["commitId"])
            except IndexError, KeyError:
                pass

            try:
                output += "Artifacts: \n"
                for artifact in data['artifacts']:
                    output += artifact['fileName'] + "\n"
            except IndexError, KeyError:
                pass

        return [output]

    def _start_build(self, job):
        url = self.jenkins_url + "/job/{0}/build?token={1}".format(
                job,
                self.config.get('Jenkins', 'jenkins_api_token')
        # Ugh. I can't seem to get the Jenkins API authentication to work via the 
        # urllib2. Resorting to using calling a Wget subprocess. Sorry. I'll
        # come back to it.
        cmds = ["/usr/bin/wget", "--spider", "--auth-no-challenge",
                "--http-user="+self.config.get('Jenkins', 'jenkins_user'), 
                "--http-password="+self.config.get('Jenkins', 'jenkins_password'),
                "--no-proxy",
               url]
        try:
            subprocess.call(cmds, shell=False)
        except:
            output = "Failed to start build"
        else:
            output = "Build started"

        return [output]

    def run(self, action, data):
        output = []
        if action == 'last':
            if data:
                jobname = data
                output = self._get_last_build(jobname)
            else:
                output.append("Please specify a job")
        elif action == 'jobs':
            search = data
            output = self._list_jobs_like(search)
        elif action == 'build':
            if data: 
                jobname = data
                output = self._start_build(jobname)
            else:
                output.append("Please specify a job")

        if output:
            for out in output:
                self.speak(out)
        else:
            self.speak("Dunno what you mean sorry.")


if __name__ == '__main__':
    jenkins = Jenkins()
    #print jenkins._list_jobs_like("bpl-www")
    job = "bpl-www-site-php5"
    print jenkins._get_last_build(job)
    #print jenkins._start_build("bpl-www-site-php5")
