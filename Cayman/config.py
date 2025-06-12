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
    _ = PluginInternationalization('Cayman')
except Exception:
    def _(x):
        return x


def configure(advanced):
    from supybot.questions import output
    conf.registerPlugin('Cayman', True)
    if advanced:
        output(_('The Cayman plugin displays cat gifs or facts in channels.'))


Cayman = conf.registerPlugin('Cayman')

conf.registerChannelValue(
    Cayman,
    'enable',
    registry.Boolean(False, _('Turns the plugin on/off')),
)
conf.registerChannelValue(
    Cayman,
    'timeout',
    registry.Float(5.0, _('Fetch timeout in seconds')),
)
conf.registerChannelValue(
    Cayman,
    'linkChance',
    registry.Integer(67, _('0-100 chance to trigger a link to a cat gif')),
)
conf.registerChannelValue(
    Cayman,
    'factChance',
    registry.Integer(33, _('0-100 chance to trigger a cat fact')),
)
conf.registerChannelValue(
    Cayman,
    'throttle',
    registry.Integer(60, _('Will only trigger if it has been X seconds since the last trigger')),
)
conf.registerChannelValue(
    Cayman,
    'triggerWords',
    registry.CommaSeparatedListOfStrings(
        ['meow', 'cat', 'cats', 'kitten', 'kittens'],
        _('List of words that may trigger facts or links'),
    ),
)
conf.registerChannelValue(
    Cayman,
    'prefixNick',
    registry.Boolean(True, _('Whether to include nick prefix in command replies')),
)

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
