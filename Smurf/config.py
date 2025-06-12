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
    _ = PluginInternationalization('Smurf')
except Exception:
    def _(x):
        return x


def configure(advanced):
    from supybot.questions import output
    conf.registerPlugin('Smurf', True)
    if advanced:
        output(_('The Smurf fetches URL titles'))


Smurf = conf.registerPlugin('Smurf')

conf.registerChannelValue(
    Smurf,
    'enable',
    registry.Boolean(False, _('Should URL smurfing be enabled in this channel?')),
)
conf.registerChannelValue(
    Smurf,
    'timeout',
    registry.Float(5.0, _('Fetch timeout in seconds')),
)
conf.registerChannelValue(
    Smurf,
    'reportErrors',
    registry.Boolean(False, _('Whether to report errors')),
)
conf.registerChannelValue(
    Smurf,
    'showRedirectChain',
    registry.Boolean(False, _('Whether to display full redirect chain in hostnames'))
)
conf.registerChannelValue(
    Smurf,
    'smurfMultipleURLs',
    registry.Boolean(False, _('Whether to smurf multiple URLs in a message')),
)
conf.registerChannelValue(
    Smurf,
    'ignoreUrlRegexp',
    registry.Regexp(None, _('Ignore URL regexp')),
)

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
