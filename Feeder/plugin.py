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
from requests.adapters import HTTPAdapter
from requests.sessions import Session
from feedparser import parse as parse_feed, USER_AGENT as DEFAULT_USER_AGENT
from urllib3 import Retry

from supybot import callbacks, conf, ircmsgs, world
from supybot.commands import wrap
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Feeder')
except ImportError:
    def _(x):
        return x


HistoryFilename = conf.supybot.directories.data.dirize('Feeder.flat')


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
        history = self.load_history()

        for feed in feeds:
            try:
                timeout = self.registryValue('timeout')
                if 'timeout' in feeds[feed]:
                    timeout = feeds[feed]['timeout']

                headers = conf.defaultHttpHeaders(None, None)
                headers['User-Agent'] = DEFAULT_USER_AGENT
                if 'user_agent' in feeds[feed]:
                    headers['User-Agent'] = feeds[feed]['user_agent']

                sess = Session()
                retries = Retry(connect=5, read=5, redirect=5, status=5, other=5, backoff_factor=1.0)
                sess.mount('http://', HTTPAdapter(max_retries=retries))

                with sess.get(feeds[feed]['url'], timeout=timeout, headers=headers) as response:
                    text = response.text

                response = parse_feed(text)
            except Exception as e:
                self.log.error('Feeder :: Error refreshing feed %s :: %s: %s', feed, str(type(e)), e)
                continue
            finally:
                sess.close()    # pyright:ignore[reportPossiblyUnboundVariable]

            entries = response['entries']

            if 'ignore' in feeds[feed]:
                try:
                    regexp = re.compile(feeds[feed]['ignore'])
                    entries = [entry for entry in entries if not regexp.search(entry['title'])]
                except re.PatternError:
                    pass

            for irc in world.ircs:
                limit = self.registryValue('lastN', network=irc.network)
                last_n = entries[0:limit]
                last_n.reverse()

                for channel in self.registryValue('announces', network=irc.network):
                    for entry in last_n:
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
                        if network not in history:
                            history[network] = {}

                        channel = str(channel)
                        if channel not in history[network]:
                            history[network][channel] = {}

                        if feed not in history[network][channel]:
                            history[network][channel][feed] = []

                        entry_id = None
                        if 'id' in entry:
                            entry_id = entry['id']
                        else:
                            entry_id = entry['link']

                        if entry_id not in history[network][channel][feed]:
                            history[network][channel][feed].insert(0, entry_id)

                            msg = fmt.format_map(entry)
                            irc.queueMsg(ircmsgs.privmsg(channel, msg))

        self.save_history(history)

    def load_history(self):
        try:
            with open(HistoryFilename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def save_history(self, history):
        feeds = self.registryValue('feeds')

        for network in history:
            irc = world.getIrc(network)

            if not irc:
                del history[network]
            else:
                for channel in history[network]:
                    if not channel in irc.state.channels:
                        del history[network][channel]
                    else:
                        for feed in history[network][channel]:
                            if not feeds[feed]:
                                del history[network][channel][feed]

        for network in history:
            limit = self.registryValue('history', network=network)

            for channel in history[network]:
                for feed in history[network][channel]:
                    if len(history[network][channel][feed]) > limit:
                        history[network][channel][feed] = history[network][channel][feed][0:limit]

        try:
            with open(HistoryFilename, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2)
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
            os.remove(HistoryFilename)
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

            irc.replySuccess()

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

                Removes a feed'''

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

                Sets a feed metadata field. One of: title, format, timeout, ignore, url, user_agent'''

                if key not in ['title', 'format', 'timeout', 'ignore', 'url', 'user_agent']:
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
                elif key == 'timeout':
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
                    announces[channel] = list(dict.fromkeys(announces.get(channel, []) + [name]))

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
                    history = plugin.load_history()

                    if network in history:
                        if channel in history[network]:
                            if name in history[network][channel]:
                                del history[network][channel][name]

                    plugin.save_history(history)

                    irc.replySuccess()

            @wrap([
                'admin'
            ])
            def sanitize(self, irc, _msg, _args):
                '''no arguments

                Sanitizes the announces configuration'''

                plugin = irc.getCallback('Feeder')

                with plugin.registryValue('announces', network=irc.network, value=False).editable() as announces:
                    for channel in announces.copy():
                        if channel not in irc.state.channels:
                            del announces[channel]

                irc.replySuccess()

        class announce(announces):
            def listCommands(self, pluginCommands=...):
                return []


Class = Feeder

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
