import subprocess
import json

from GiantDwarf import GiantDwarfPlugin
from lib import utils
import settings


class Jenkins(GiantDwarfPlugin):
    def __init__(self):
        super(Jenkins, self).__init__()
        self.jenkins_url = settings.JENKINS_DOMAIN

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
                settings.JENKINS_API_TOKEN)
        # Ugh. I can't seem to get the Jenkins API authentication to work via the 
        # urllib2. Resorting to using calling a Wget subprocess. Sorry. I'll
        # come back to it.
        cmds = ["/usr/bin/wget", "--spider", "--auth-no-challenge",
                "--http-user="+settings.JENKINS_USER, 
                "--http-password="+settings.JENKINS_PASSWORD,
                "--no-proxy",
               url]
        try:
            subprocess.call(cmds, shell=False)
        except:
            output = "Failed to start build"
        else:
            output = "Build started"

        return [output]

    def run(self, data, room):
        output = []
        if " ".join(data).startswith("last"):
            if len(data) > 1: 
                jobname = data[1]
                output = self._get_last_build(jobname)
            else:
                output.append("Please specify a job")
        elif " ".join(data).startswith("jobs like"):
            search = data[2]
            output = self._list_jobs_like(search)
        elif " ".join(data).startswith("build"):
            if len(data) > 1: 
                jobname = data[1]
                output = self._start_build(jobname)
            else:
                output.append("Please specify a job")

        if output:
            for out in output:
                room.speak(out)
        else:
            room.speak("Dunno what you mean sorry.")


if __name__ == '__main__':
    jenkins = Jenkins()
    #print jenkins._list_jobs_like("bpl-www")
    job = "bpl-www-site-php5"
    print jenkins._get_last_build(job)
    #print jenkins._start_build("bpl-www-site-php5")