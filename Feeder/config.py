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
# pylint:disable=missing-function-docstring
# pylint:disable=import-outside-toplevel
# pylint:disable=broad-exception-caught

from supybot import conf, registry

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Feeder')
except Exception:
    def _(x):
        return x


def configure(advanced):
    from supybot.questions import output
    conf.registerPlugin('Feeder', True)
    if advanced:
        output(_('The Feeder scans RSS feeds.'))


Feeder = conf.registerPlugin('Feeder')

conf.registerGlobalValue(
    Feeder,
    'feeds',
    registry.Json({}, _('JSON-serialized configuration of feeds, custom titles, formats, etc')),
)
conf.registerGlobalValue(
    Feeder,
    'schedule',
    registry.String('*/5 * * * *', _('Cron schedule when to poll feeds.')),
)
conf.registerGlobalValue(
    Feeder,
    'timeout',
    registry.Float(5.0, _('Fetch timeout in seconds')),
)
conf.registerNetworkValue(
    Feeder,
    'format',
    registry.String('RSS :: {feed} :: {title} :: {link}', _('Default announce format')),
)
conf.registerNetworkValue(
    Feeder,
    'lastN',
    registry.Integer(5, _('Maximum number of messages to announce')),
)
conf.registerNetworkValue(
    Feeder,
    'history',
    registry.Integer(100, _('Number of entries to keep in announced history database')),
)
conf.registerNetworkValue(
    Feeder,
    'announces',
    registry.Json({}, _('JSON-serialized configuration of channels feeds are announced to')),
)

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
