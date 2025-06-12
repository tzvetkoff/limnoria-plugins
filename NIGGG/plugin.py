###
# Copyright (c) 2025 Latchezar Tzvetkoff
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###

# pylint:disable=missing-module-docstring
# pylint:disable=missing-class-docstring
# pylint:disable=missing-function-docstring
# pylint:disable=too-many-ancestors
# pylint:disable=too-many-arguments
# pylint:disable=bare-except

import json
import os
from xml.etree import ElementTree

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from requests import get

from supybot import callbacks, conf, ircmsgs, world
from supybot.commands import wrap
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('NIGGG')
except ImportError:
    def _(x):
        return x


AnnouncedFilename = conf.supybot.directories.data.dirize('NIGGG.flat')


class NIGGG(callbacks.Plugin):
    '''Sends notifications about earthquakes around Bulgaria, data from https://ndc.niggg.bas.bg/'''
    threaded = True
    job_scheduler = None

    def __init__(self, irc):
        '''Initialize the plugin internal variables'''
        super().__init__(irc)
        self.scheduler_start()

    def die(self):
        self.scheduler_stop()

    def refresh(self):
        announced = self.load_announced()
        events = self.fetch_data()
        last = events[0]

        if last['id'] in announced:
            return

        announced.append(last['id'])
        self.save_announced(announced)

        for irc in world.ircs:
            for channel in list(irc.state.channels):
                if self.registryValue('enable', channel, irc.network):
                    message_format = self.registryValue('messageFormat', channel, irc.network)
                    message = message_format.format_map(last)
                    irc.queueMsg(ircmsgs.privmsg(channel, message))

    def fetch_data(self):
        response = get('https://ndc.niggg.bas.bg/data.xml', timeout=self.registryValue('timeout')).text
        tree = ElementTree.fromstring(response)

        result = []
        for marker in tree.iter('marker'):
            attributes = marker.attrib
            del attributes['date']
            del attributes['area']
            del attributes['location']

            result.append(attributes)

        return result

    def load_announced(self):
        try:
            with open(AnnouncedFilename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    def save_announced(self, announced):
        try:
            with open(AnnouncedFilename, 'w', encoding='utf-8') as f:
                json.dump(announced, f)
        except:
            pass

    @wrap([
        'admin',
        ('literal', {'start', 'stop', 'restart', 'refresh'}),
    ])
    def scheduler(self, _irc, _msg, _args, op):
        '''[start|stop|restart]

        Starts/stops/restarts the scheduler.'''

        {
            'start':   self.scheduler_start,
            'stop':    self.scheduler_stop,
            'restart': self.scheduler_restart,
            'refresh': self.scheduler_refresh,
        }[op]()

    def scheduler_start(self):
        if self.job_scheduler is None:
            self.job_scheduler = BackgroundScheduler()

            schedule = self.registryValue('schedule')
            self.job_scheduler.add_job(self.refresh, CronTrigger.from_crontab(schedule), id='niggg_refresh')

            self.job_scheduler.start()

    def scheduler_stop(self):
        if self.job_scheduler is not None:
            self.job_scheduler.shutdown(wait=False)
            self.job_scheduler = None

    def scheduler_restart(self):
        self.scheduler_stop()
        self.scheduler_start()

    def scheduler_refresh(self):
        try:
            os.remove(AnnouncedFilename)
        except:
            pass

        self.refresh()


Class = NIGGG

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
