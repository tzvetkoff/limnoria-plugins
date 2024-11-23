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
# pylint:disable=too-many-arguments

import json
from requests import get

from supybot import callbacks
from supybot.commands import optional, wrap
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('BinanceTicker')
except ImportError:
    def _(x):
        return x


class BinanceTicker(callbacks.Plugin):
    '''Fetches crypto currency prices from Binance's ticker'''
    threaded = True

    @wrap([
        optional('float'),
        'somethingWithoutSpaces',
        optional(('literal', {'to', 'TO', 'in', 'IN', '=>'})),
        optional('somethingWithoutSpaces'),
    ])
    def rate(self, irc, msg, _args, count, currency, _, target):
        '''[count] <currency> [to [target currency]]

        Fetches crypto currency's price from https://rate.sx/
        '''
        if count is None:
            count = 1.0
        if target is None:
            target = 'USD'

        currency = currency.upper()
        target = target.upper()

        symbol = f'{currency}{target}'
        if target == 'USD':
            symbol = f'{symbol}T'

        url = f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}'
        timeout = self.registryValue('timeout', msg.channel, irc.network)

        text = str(get(url, timeout=timeout).text)
        try:
            response = json.loads(text)
        except json.JSONDecodeError as e:
            irc.reply(f'ERROR: {e}')
            return

        if 'code' in response and 'msg' in response:
            irc.reply(f'ERROR: {response['msg']}')
            return

        irc.reply(f'{count} {currency} = {response['price']} {target}')


Class = BinanceTicker

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
