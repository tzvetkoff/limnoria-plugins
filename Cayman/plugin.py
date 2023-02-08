###
# Copyright (c) 2023 Latchezar Tzvetkoff
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

from supybot import callbacks, ircmsgs, utils
from supybot.commands import optional, wrap
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('RateSX')
except ImportError:
    def _(x):
        return x

import random
import datetime
import os
import re
import json
import requests


class Cayman(callbacks.Plugin):
    '''Displays cat facts or cat gifs based on probability'''

    threaded = True
    last_message_timestamp = False

    def _gif(self):
        response = requests.get('http://edgecats.net/random')
        return response.text

    def _fact(self):
        response = requests.get('https://catfact.ninja/fact')
        data = json.loads(response.text)
        return data['fact']

    def _matches_trigger_words(self, message):
        words = [word.strip() for word in self.registryValue('triggerWords')]
        pattern = re.compile(r'\b(' + '|'.join(words) + r')\b', re.IGNORECASE)
        return not not pattern.search(message)

    @wrap([])
    def catgif(self, irc, msg, args):
        '''Gets a random cat gif'''
        irc.reply(self._gif())

    @wrap([])
    def catfact(self, irc, msg, args):
        '''Gets a random cat fact'''
        irc.reply(self._fact())

    def doPrivmsg(self, irc, msg):
        if not msg.channel:
            return
        if msg.repliedTo:
            return
        if not self.registryValue('enable', msg.channel, irc.network):
            return
        if ircmsgs.isCtcp(msg) and not ircmsgs.isAction(msg):
            return
        if not self._matches_trigger_words(msg.args[1]):
            return

        now = datetime.datetime.now()
        last_message_timestamp = self.last_message_timestamp
        self.last_message_timestamp = now

        if last_message_timestamp:
            seconds_since_last_message = (now - last_message_timestamp).total_seconds()
            if seconds_since_last_message < self.registryValue('throttle'):
                self.log.info('Cayman throttled.')
                return

        link_chance = self.registryValue('linkChance')
        fact_chance = self.registryValue('factChance')

        link_rand = random.randrange(0, 100) <= link_chance
        fact_rand = random.randrange(0, 100) <= fact_chance

        if link_rand:
            irc.reply(self._gif(), prefixNick=False)
        elif fact_rand:
            irc.reply(self._fact(), prefixNick=False)


Class = Cayman

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
