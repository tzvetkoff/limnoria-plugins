###
# Copyright (c) 2026 Latchezar Tzvetkoff
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

import json
import requests

from supybot import callbacks
from supybot.commands import optional, wrap
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Fuelo')
except ImportError:
    def _(x):
        return x


class Fuelo(callbacks.Plugin):
    '''Fetches fuel (gasoline, diesel, lpg, methane) price'''
    threaded = True

    @wrap([
        ('literal', {'gasoline', 'diesel', 'lpg', 'methane'}),
        optional('somethingWithoutSpaces'),
    ])
    def fuelo(self, irc, msg, _args, fuel, date):
        '''<fuel> [date]

        Fetches fuel (gasoline, diesel, lpg, methane) price'''

        api_key = self.registryValue('apiKey', msg.channel, irc.network)
        if not api_key:
            irc.reply('ERROR: API key not set')
            return

        timeout = self.registryValue('timeout', msg.channel, irc.network)

        url = f'https://fuelo.net/api/price?key={api_key}&fuel={fuel}'
        if date is not None:
            url = f'{url}&date={date}'

        with requests.get(url, timeout=timeout) as response:
            text = str(response.text)

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            irc.reply(f'ERROR: {e}')
            return

        if 'status' in data and data['status'] == 'error':
            irc.reply(f'ERROR: {data['error_message']}')
            return

        irc.reply(f'{data['price']} {data['dimension']}')


Class = Fuelo

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
