###
# Copyright (c) 2024 Latchezar Tzvetkoff
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

import random
import datetime
import re
import json
import requests

from supybot import callbacks, ircmsgs
from supybot.commands import wrap
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Cayman')
except ImportError:
    def _(x):
        return x


class Cayman(callbacks.Plugin):
    '''Displays cat gifs or facts in channels'''

    threaded = True
    last_message_timestamp = False

    def _gif(self, channel, network):
        response = requests.get('http://edgecats.net/random', timeout=self.registryValue('timeout', channel, network))
        return response.text.replace('http://', 'https://')

    def _fact(self, channel, network):
        response = requests.get('https://catfact.ninja/fact', timeout=self.registryValue('timeout', channel, network))
        data = json.loads(response.text)
        return data['fact']

    def _match(self, message, channel, network):
        words = [word.strip() for word in self.registryValue('triggerWords', channel, network)]
        pattern = re.compile(r'\b(' + '|'.join(words) + r')\b', re.IGNORECASE)
        return pattern.search(message)

    @wrap
    def catgif(self, irc, msg, _args):
        '''Gets a random cat gif'''
        irc.reply(
            self._gif(msg.channel, irc.network),
            prefixNick=self.registryValue('prefixNick', msg.channel, irc.network)
        )

    @wrap
    def catfact(self, irc, msg, _args):
        '''Gets a random cat fact'''
        irc.reply(
            self._fact(msg.channel, irc.network),
            prefixNick=self.registryValue('prefixNick', msg.channel, irc.network)
        )

    def doPrivmsg(self, irc, msg):
        if not msg.channel:
            return
        if msg.repliedTo:
            return
        if not self.registryValue('enable', msg.channel, irc.network):
            return
        if ircmsgs.isCtcp(msg) and not ircmsgs.isAction(msg):
            return
        if not self._match(msg.args[1], msg.channel, irc.network):
            return

        now = datetime.datetime.now()
        last_message_timestamp = self.last_message_timestamp
        self.last_message_timestamp = now

        if last_message_timestamp:
            seconds_since_last_message = (now - last_message_timestamp).total_seconds()
            if seconds_since_last_message < self.registryValue('throttle', msg.channel, irc.network):
                self.log.info('Cayman throttled.')
                return

        link_chance = self.registryValue('linkChance', msg.channel, irc.network)
        fact_chance = self.registryValue('factChance', msg.channel, irc.network)

        link_rand = random.randrange(1, 101) <= link_chance
        fact_rand = random.randrange(1, 101) <= fact_chance

        if link_rand:
            irc.reply(self._gif(msg.channel, irc.network), prefixNick=False)
        elif fact_rand:
            irc.reply(self._fact(msg.channel, irc.network), prefixNick=False)


Class = Cayman

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
