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


from supybot import conf
import supybot.registry as registry
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Gitea')
except Exception:
    def _(x):
        return x


def configure(advanced):
    from supybot.questions import output
    conf.registerPlugin('Gitea', True)
    if advanced:
        output('Gitea webhooks integration')


Gitea = conf.registerPlugin('Gitea')

conf.registerGlobalValue(
    Gitea,
    'debug',
    registry.Boolean(False, _('Whether to dump and save each webhook request in ${PLUGIN_DIR}/debug')),
)
conf.registerGlobalValue(
    Gitea,
    'webhooks',
    registry.String('', _('Webhooks configuration. You\'re not supposed to edit this by hand.')),
)
conf.registerGlobalValue(
    Gitea,
    'errors',
    registry.Boolean(False, _('Whether to display errors in HTTP response.')),
)

conf.registerGroup(Gitea, 'format')

conf.registerChannelValue(
    Gitea.format,
    'create',
    registry.String('', _('Message format for "create" webhook event.')),
)
conf.registerChannelValue(
    Gitea.format,
    'delete',
    registry.String('', _('Message format for "delete" webhook event.')),
)
conf.registerChannelValue(
    Gitea.format,
    'fork',
    registry.String('', _('Message format for "fork" webhook event.')),
)
conf.registerChannelValue(
    Gitea.format,
    'issue_comment',
    registry.String('', _('Message format for "issue_comment" webhook event.')),
)
conf.registerChannelValue(
    Gitea.format,
    'issues',
    registry.String('', _('Message format for "issues" webhook event.')),
)
conf.registerChannelValue(
    Gitea.format,
    'pull_request_approved',
    registry.String('', _('Message format for "pull_request_approved" webhook event.')),
)
conf.registerChannelValue(
    Gitea.format,
    'pull_request_rejected',
    registry.String('', _('Message format for "pull_request_rejected" webhook event.')),
)
conf.registerChannelValue(
    Gitea.format,
    'pull_request',
    registry.String('', _('Message format for "pull_request" webhook event.')),
)
conf.registerChannelValue(
    Gitea.format,
    'push',
    registry.String('', _('Message format for "push" webhook event.')),
)
conf.registerChannelValue(
    Gitea.format,
    'release',
    registry.String('', _('Message format for "release" webhook event.')),
)

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
