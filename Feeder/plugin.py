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
# pylint:disable=too-many-branches
# pylint:disable=too-many-nested-blocks
# pylint:disable=too-many-locals
# pylint:disable=bare-except
# pylint:disable=invalid-name
# pylint:disable=broad-exception-caught


import json
import os
import re

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from requests import get
from feedparser import parse

from supybot import callbacks, conf, ircmsgs, world
from supybot.commands import wrap
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Feeder')
except ImportError:
    def _(x):
        return x


AnnouncedFilename = conf.supybot.directories.data.dirize('Feeder.flat')


class Feeder(callbacks.Plugin):
    '''RSS/Atom feed scanner.'''
    threaded = True
    job_scheduler = None

    def __init__(self, irc):
        '''Initialize the plugin internal variables'''
        super().__init__(irc)
        self.scheduler_start()

    def die(self):
        self.scheduler_stop()

    def refresh(self):
        feeds = self.registryValue('feeds')
        announced = self.load_announced()

        for feed in feeds:
            try:
                timeout = self.registryValue('timeout')
                if 'timeout' in feeds[feed]:
                    timeout = feeds[feed]['timeout']

                with get(feeds[feed]['url'], timeout=timeout) as response:
                    text = response.text

                response = parse(text)
            except Exception as e:
                self.log.error('Feeder :: Error refreshing feed %s :: %s: %s', feed, str(type(e)), e)
                continue

            entries = response['entries']

            for irc in world.ircs:
                with self.registryValue('announces', network=irc.network, value=False).editable() as announces:
                    for channel in announces:
                        if channel not in irc.state.channels:
                            del announces[channel]
                            continue

                        if feed in announces[channel]:
                            last_n = self.registryValue('lastN', network=irc.network)
                            last_n_entries = entries[0:last_n]

                            for entry in last_n_entries:
                                if 'ignore' in feeds[feed]:
                                    regexp = re.compile(feeds[feed]['ignore'])
                                    if regexp.match(entry['title']):
                                        continue

                                if 'summary' in entry:
                                    del entry['summary']
                                if 'content' in entry:
                                    del entry['content']

                                entry['feed'] = feed
                                if 'title' in feeds[feed]:
                                    entry['feed'] = feeds[feed]['title']

                                fmt = self.registryValue('format', network=irc.network)
                                if 'format' in feeds[feed]:
                                    fmt = feeds[feed]['format']

                                network = str(irc.network)
                                if network not in announced:
                                    announced[network] = {}

                                channel = str(channel)
                                if channel not in announced[network]:
                                    announced[network][channel] = {}

                                if feed not in announced[network][channel]:
                                    announced[network][channel][feed] = []

                                entry_id = None
                                if 'id' in entry:
                                    entry_id = entry['id']
                                else:
                                    entry_id = entry['link']

                                if entry_id not in announced[network][channel][feed]:
                                    announced[network][channel][feed].append(entry_id)

                                    msg = fmt.format_map(entry)
                                    irc.queueMsg(ircmsgs.privmsg(channel, msg))

        self.save_announced(announced)

    def load_announced(self):
        try:
            with open(AnnouncedFilename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def save_announced(self, announced):
        for network in announced:
            for channel in announced[network]:
                for feed in announced[network][channel]:
                    history = self.registryValue('history', network=network)

                    if len(announced[network][channel][feed]) > history:
                        announced[network][channel][feed] = announced[network][channel][feed][-history:]

        try:
            with open(AnnouncedFilename, 'w', encoding='utf-8') as f:
                json.dump(announced, f, indent=2)
        except:
            pass

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

    class feeder(callbacks.Commands):
        @wrap([
            'admin',
            ('literal', {'start', 'stop', 'restart', 'refresh'}),
        ])
        def scheduler(self, irc, _msg, _args, op):
            '''[start|stop|restart]

            Starts/stops/restarts the scheduler.'''

            plugin = irc.getCallback('Feeder')

            {
                'start':   plugin.scheduler_start,
                'stop':    plugin.scheduler_stop,
                'restart': plugin.scheduler_restart,
                'refresh': plugin.scheduler_refresh,
            }[op]()

        class feeds(callbacks.Commands):
            @wrap([
                'admin',
            ])
            def list(self, irc, _msg, _args):
                '''no arguments

                Lists configured feeds'''

                plugin = irc.getCallback('Feeder')
                feeds = plugin.registryValue('feeds')

                if feeds:
                    irc.reply(', '.join(feeds.keys()))
                else:
                    irc.reply(_('No feeds configured.'))

            @wrap([
                'admin',
                'somethingWithoutSpaces',
            ])
            def info(self, irc, _msg, _args, name):
                '''<name>

                Get full feed info'''

                plugin = irc.getCallback('Feeder')
                feeds = plugin.registryValue('feeds')

                if name in feeds:
                    irc.reply(json.dumps(feeds[name], separators=(',', ':')))
                else:
                    msg = _('Feed {name} not found.').format_map({
                        'name': name,
                    })
                    irc.reply(msg)

            @wrap([
                'admin',
                'somethingWithoutSpaces',
                'url'
            ])
            def add(self, irc, _msg, _args, name, url):
                '''<name> <url>

                Adds a new feed to be monitored'''

                plugin = irc.getCallback('Feeder')

                with plugin.registryValue('feeds', value=False).editable() as feeds:
                    if name in feeds:
                        msg = _('Feed {name} already exists.').format_map({
                            'name': name,
                        })
                        irc.reply(msg)
                    else:
                        feeds[name] = {
                            'url': url,
                        }
                        irc.replySuccess()


            @wrap([
                'admin',
                'somethingWithoutSpaces'
            ])
            def remove(self, irc, _msg, _args, name):
                '''<name>

                Removes a feed
                '''

                plugin = irc.getCallback('Feeder')

                with plugin.registryValue('feeds', value=False).editable() as feeds:
                    if name in feeds:
                        del feeds[name]
                        irc.replySuccess()
                    else:
                        msg = _('Feed {name} not found.').format_map({
                            'name': name,
                        })
                        irc.reply(msg)

            @wrap([
                'admin',
                'somethingWithoutSpaces',
                'somethingWithoutSpaces',
                'something',
            ])
            def set(self, irc, _msg, _args, name, key, value):
                '''<name> <key> <value>

                Sets a feed metadata field. One of: title, format, timeout, ignore, url
                '''

                if key not in ['title', 'format', 'timeout', 'ignore', 'url']:
                    msg = _('Metadata {key} not allowed.').format_map({
                        'key': key,
                    })
                    irc.reply(msg)
                    return

                plugin = irc.getCallback('Feeder')

                if key == 'ignore':
                    try:
                        re.compile(value)
                    except re.PatternError:
                        irc.reply(_('Invalid regex.'))
                        return

                if key == 'timeout':
                    try:
                        value = float(value)
                    except ValueError:
                        irc.reply(_('Invalid float.'))
                        return

                with plugin.registryValue('feeds', value=False).editable() as feeds:
                    if name in feeds:
                        feeds[name][key] = value
                        irc.replySuccess()
                    else:
                        msg = _('Feed {name} not found.').format_map({
                            'name': name,
                        })
                        irc.reply(msg)

            @wrap([
                'admin',
                'somethingWithoutSpaces',
                'somethingWithoutSpaces',
            ])
            def unset(self, irc, _msg, _args, name, key):
                '''<name> <key>

                Unsets a feed metadata field. One of: title, format, timeout, ignore.'''

                if key not in ['title', 'format', 'timeout', 'ignore']:
                    msg = _('Metadata {key} not allowed.').format_map({
                        'key': key,
                    })
                    irc.reply(msg)
                    return

                plugin = irc.getCallback('Feeder')

                with plugin.registryValue('feeds', value=False).editable() as feeds:
                    if name in feeds:
                        if key in feeds[name]:
                            del feeds[name][key]
                            irc.replySuccess()
                        else:
                            msg = _('Feed {name} metadata {key} not set.').format_map({
                                'name': name,
                                'key':  key,
                            })
                            irc.reply(msg)
                    else:
                        msg = _('Feed {name} not found.').format_map({
                            'name': name,
                        })
                        irc.reply(msg)

        class feed(feeds):
            def listCommands(self, pluginCommands=...):
                return []

        class announces(callbacks.Commands):
            @wrap([
                'admin',
            ])
            def list(self, irc, _msg, _args):
                '''No arguments

                Lists configured announces.'''

                plugin = irc.getCallback('Feeder')
                announces = plugin.registryValue('announces', network=irc.network)

                if announces:
                    irc.reply(json.dumps(announces, separators=(',', ':')))
                else:
                    irc.reply(_('No announces configured.'))

            @wrap([
                'admin',
                'somethingWithoutSpaces',
                'somethingWithoutSpaces',
            ])
            def add(self, irc, _msg, _args, channel, name):
                '''<channel> <name>

                Add a feed announce to a channel'''

                if channel not in irc.state.channels:
                    msg = _('Channel {channel} not found.').format_map({
                        'channel': channel,
                    })
                    irc.reply(msg)
                    return

                plugin = irc.getCallback('Feeder')
                feeds = plugin.registryValue('feeds')

                if name not in feeds:
                    msg = _('Feed {name} not found.').format_map({
                        'name': name,
                    })
                    irc.reply(msg)
                    return

                with plugin.registryValue('announces', network=irc.network, value=False).editable() as announces:
                    announces[channel] = list(set(announces.get(channel, []) + [name]))

                irc.replySuccess()

            @wrap([
                'admin',
                'somethingWithoutSpaces',
                'somethingWithoutSpaces',
            ])
            def remove(self, irc, _msg, _args, channel, name):
                '''<channel> <name>

                Remove a feed announce from a channel'''

                if channel not in irc.state.channels:
                    msg = _('Channel {channel} not found.').format_map({
                        'channel': channel,
                    })
                    irc.reply(msg)
                    return

                plugin = irc.getCallback('Feeder')
                feeds = plugin.registryValue('feeds')

                if name not in feeds:
                    msg = _('Feed {name} not found.').format_map({
                        'name': name,
                    })
                    irc.reply(msg)
                    return

                with plugin.registryValue('announces', network=irc.network, value=False).editable() as announces:
                    if name not in announces.get(channel, []):
                        msg = _('Feed {name} not announced in {channel}.').format_map({
                            'name':    name,
                            'channel': channel,
                        })
                        irc.reply(msg)
                    else:
                        announces[channel].remove(name)
                        if announces[channel] == []:
                            del announces[channel]

                        irc.replySuccess()

            @wrap([
                'admin',
                'somethingWithoutSpaces',
                'somethingWithoutSpaces',
            ])
            def reset(self, irc, _msg, _args, channel, name):
                '''<channel> <name>

                Resets announced database for a channel'''

                if channel not in irc.state.channels:
                    msg = _('Channel {channel} not found.').format_map({
                        'channel': channel,
                    })
                    irc.reply(msg)
                    return

                plugin = irc.getCallback('Feeder')
                feeds = plugin.registryValue('feeds')

                if name not in feeds:
                    msg = _('Feed {name} not found.').format_map({
                        'name': name,
                    })
                    irc.reply(msg)
                    return

                announces = plugin.registryValue('announces', network=irc.network)

                if name not in announces.get(channel, []):
                    msg = _('Feed {name} not announced in {channel}.').format_map({
                        'name':    name,
                        'channel': channel,
                    })
                    irc.reply(msg)
                else:
                    network = str(irc.network)
                    channel = str(channel)
                    announced = plugin.load_announced()

                    if network in announced:
                        if channel in announced[network]:
                            if name in announced[network][channel]:
                                del announced[network][channel][name]

                    plugin.save_announced(announced)

                    irc.replySuccess()

        class announce(announces):
            def listCommands(self, pluginCommands=...):
                return []


Class = Feeder

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
