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

from supybot import callbacks, httpserver, ircmsgs, world
from supybot.commands import wrap
import json
import os
import time
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Gitea')
except ImportError:
    def _(x):
        return x


class Dict(dict):
    def __missing__(self, key):
        return '{' + str(key) + '}'


class GiteaWebhookCallback(httpserver.SupyHTTPServerCallback):
    name = 'GitHub announce callback'
    defaultResponse = 'OK'

    def __init__(self, plugin):
        self.plugin = plugin
        pass

    def flattenDict(self, kv, result=None, memo=None):
        if result is None:
            result = {}
        if memo is None:
            memo = []

        for k in kv:
            v = kv[k]
            if isinstance(v, list):
                v = dict(enumerate(v))

            if isinstance(v, dict):
                result['__'.join(memo + ['#len'])] = len(v)
                self.flattenDict(v, result, memo + [str(k)])
            else:
                result['__'.join(memo + [str(k)])] = v

        return result

    def getHeader(self, name):
        name = name.lower()
        for k in self.headers:
            if str(k).lower() == name:
                return self.headers[k]

    def doDefault(self, handler, path, write_content):
        response = self.defaultResponse.encode()
        handler.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8; charset=utf-8')
        self.send_header('Content-Length', len(response))
        self.end_headers()
        if write_content:
            self.wfile.write(response)

    def doError(self, handler, path, code=500, error='Internal server error', write_content=True):
        if self.plugin.registryValue('errors'):
            response = str(error).encode()
            handler.send_response(code)
            self.send_header('Content-Type', 'text/plain; charset=utf-8; charset=utf-8')
            self.send_header('Content-Length', len(response))
            self.end_headers()
            if write_content:
                self.wfile.write(response)
        else:
            self.doDefault(handler, path, write_content)

    def doWellKnown(self, handler, path):
        self.doError(handler, path, 404, 'File not found')

    def doGet(self, handler, path):
        self.doError(handler, path, 405, 'Method not allowed')

    def doHead(self, handler, path):
        self.doError(handler, path, 405, 'Method not allowed', False)

    def doPost(self, handler, path, form):
        path = path.strip('/')
        webhooks = self.plugin._read()
        if path not in webhooks:
            self.doError(handler, path, 403, 'Webhook not found')
            return

        network = webhooks[path]['network']
        channel = webhooks[path]['channel']

        delivery = self.getHeader('X-Gitea-Delivery')
        event = self.getHeader('X-Gitea-Event')
        if delivery is None or event is None:
            self.doError(handler, path, 403, 'Missing required headers')
            return

        try:
            payload = json.loads(form.decode('utf8'))
        except json.decoder.JSONDecodeError as e:
            self.doError(handler, path, 400, e)
            return

        try:
            payload = self.flattenDict(payload)
            self.handleWithMessage(handler, path, network, channel, event, payload)
        except Exception as e:
            self.doError(handler, path, 500, e)

    def handleWithMessage(self, handler, path, network, channel, event, payload):
        irc = world.getIrc(network)
        if not irc:
            raise Exception('Cannot find IRC network for this webhook')

        if channel not in irc.state.channels:
            raise Exception('Cannot find IRC channel for this webhook')

        if self.plugin.registryValue('debug'):
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S %z')
            dirpath = os.path.join(os.path.filename(__file__), 'debug')
            os.makedirs(dirpath, 0o755, True)
            filepath = os.path.join(dirpath, f'{event}-{timestamp}.json')
            with open(filepath, 'w+') as f:
                f.write(json.dumps(payload, indent=2, sort_keys=True))

        message = self.plugin.registryValue(f'format.{event}', network=network, channel=channel).strip()
        if message:
            payload = payload | {
                'b': '\u0002',
                'i': '\u001d',
                'u': '\u001f',
                's': '\u001e',
                't': '\u0011',
                'c': '\u0003',
            }
            message = str(message).format_map(Dict(payload))
            irc.sendMsg(ircmsgs.privmsg(channel, message))

        self.doDefault(handler, path, True)


class Gitea(callbacks.Plugin):
    '''Gitea webhooks integration'''
    threaded = True

    def __init__(self, irc):
        super(Gitea, self).__init__(irc)
        httpserver.hook('gitea', GiteaWebhookCallback(self))

    def die(self):
        httpserver.unhook('gitea')

    def _read(self):
        webhooks = self.registryValue('webhooks')
        try:
            return json.loads(webhooks)
        except json.decoder.JSONDecodeError:
            return {}

    def _write(self, webhooks):
        self.setRegistryValue('webhooks', json.dumps(webhooks))

    @wrap([
        'somethingWithoutSpaces',
        'channel',
    ])
    def add(self, irc, msg, args, webhook, channel):
        '''<webhook> <channel>

        Adds a new webhook at ${PUBLIC_URL}/gitea/<webhook> for #<channel>.
        '''
        if '/' in webhook:
            irc.reply('Webhook cannot contain "/".')
            return

        webhooks = self._read()
        if webhook in webhooks:
            c = webhooks[webhook]['channel']
            irc.reply(f'Webhook "{webhook}" is already configured for {c}.')
            return

        webhooks[webhook] = {
            'network': irc.network,
            'channel': channel,
        }
        self._write(webhooks)
        irc.reply(f'Webhook {webhook} added for channel {channel}.')

    @wrap([
        'somethingWithoutSpaces',
    ])
    def remove(self, irc, msg, args, webhook):
        '''<webhook>

        Removes a webhook.
        '''
        webhooks = self._read()
        if webhooks not in webhooks:
            irc.reply(f'Webhook "{webhook}" not found.')
            return

        del webhooks[webhook]
        self._write(webhooks)
        irc.reply(f'Webhook "{webhook}" removed.')

    @wrap
    def list(self, irc, msg, args):
        '''

        Lists webhooks.
        '''
        webhooks = self._read()
        if webhooks:
            for webhook in webhooks:
                network = webhooks[webhook]['network']
                channel = webhooks[webhook]['channel']
                irc.reply(f'"{webhook}": {network}/{channel}')
        else:
            irc.reply('No webhooks found.')


Class = Gitea

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
