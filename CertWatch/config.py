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
# pylint:disable=missing-function-docstring
# pylint:disable=import-outside-toplevel
# pylint:disable=broad-exception-caught

from supybot import conf, registry

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('CertWatch')
except Exception:
    def _(x):
        return x


def configure(advanced):
    from supybot.questions import output
    conf.registerPlugin('CertWatch', True)
    if advanced:
        output('The CertWatch sends notifications about expiring certificates.')


CertWatch = conf.registerPlugin('CertWatch')

conf.registerChannelValue(
    CertWatch,
    'hosts',
    registry.SpaceSeparatedSetOfStrings(
        set(),
        'List of hosts (or host:port) to scan TLS certificates from',
    ),
)
conf.registerChannelValue(
    CertWatch,
    'messageFormatExpiringMany',
    registry.String(
        _('Certificate for {cn} will expire in {days} days! ({not_after_str})'),
        _('Notification message format for certificates expiring in more than 1 day'),
    )
)
conf.registerChannelValue(
    CertWatch,
    'messageFormatExpiringOne',
    registry.String(
        _('Certificate for {cn} will expire tomorrow! ({not_after_str})'),
        _('Notification message format for certificates expiring in 1 day'),
    )
)
conf.registerChannelValue(
    CertWatch,
    'messageFormatExpiringZero',
    registry.String(
        _('Certificate for {cn} will expire today! ({not_after_str})'),
        _('Notification message format for certificates expiring today'),
    )
)
conf.registerChannelValue(
    CertWatch,
    'messageFormatExpired',
    registry.String(
        _('Certificate for {cn} has expired {days} ago! ({not_after_str})'),
        _('Notification message format for expired certificates'),
    )
)
conf.registerGlobalValue(
    CertWatch,
    'schedule',
    registry.String('12:30', _('Time (H:M) schedule when to poll certificates')),
)
conf.registerGlobalValue(
    CertWatch,
    'timeout',
    registry.Float(5.0, _('Fetch timeout in seconds')),
)

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
