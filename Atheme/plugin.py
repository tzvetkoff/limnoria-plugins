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

# pylint:disable=invalid-name
# pylint:disable=missing-module-docstring
# pylint:disable=missing-class-docstring
# pylint:disable=missing-function-docstring
# pylint:disable=too-many-ancestors
# pylint:disable=too-many-arguments

from re import search

from supybot import callbacks, ircmsgs
from supybot.commands import ircutils
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Atheme')
except ImportError:
    def _(x):
        return x


class Atheme(callbacks.Plugin):
    '''Atheme services integration'''
    threaded = True

    def __init__(self, irc):
        '''Initialize the plugin internal variables'''
        super().__init__(irc)
        self.recoveredChannels = []

    def do471(self, irc, msg):
        '''ERR_CHANNELISFULL - Clear +l mode'''
        channel = msg.args[1]
        if not self.registryValue('ChanServ.enable', channel, irc.network):
            return

        self.log.info('Channel %s on %s is full, requesting recover from ChanServ', channel, irc.network)
        if self.registryValue('ChanServ.unrecover', channel, irc.network):
            key = f'{channel}/{irc.network}'
            self.recoveredChannels.append(key)
        irc.sendMsg(self._chanserv(('RECOVER', channel)))

    def do473(self, irc, msg):
        '''ERR_INVITEONLYCHAN - Request invite from ChanServ'''
        channel = msg.args[1]
        if not self.registryValue('ChanServ.enable', channel, irc.network):
            return

        self.log.info('Channel %s on %s is invite-only, requesting invite from ChanServ', channel, irc.network)
        irc.sendMsg(self._chanserv(('INVITE', channel)))

    def do474(self, irc, msg):
        '''ERR_BANNEDFROMCHAN - Request unban from ChanServ'''
        channel = msg.args[1]
        if not self.registryValue('ChanServ.enable', channel, irc.network):
            return

        self.log.info('Banned on channel %s on %s, requesting unban from ChanServ', channel, irc.network)
        irc.sendMsg(self._chanserv(('UNBAN', channel)))

    def do475(self, irc, msg):
        '''ERR_BADCHANNELKEY - Request key from ChanServ'''
        channel = msg.args[1]
        if not self.registryValue('ChanServ.enable', channel, irc.network):
            return

        self.log.info('Channel %s on %s is keyed, requesting key from ChanServ', channel, irc.network)
        irc.sendMsg(self._chanserv(('GETKEY', channel)))

    def doMode(self, irc, msg):
        '''Opped / deopped event hooks'''
        channel = msg.channel
        if not self.registryValue('ChanServ.enable', channel, irc.network):
            return

        for (mode, arg) in ircutils.separateModes(msg.args[1:]):
            if mode == '+o' and ircutils.strEqual(arg, irc.nick):
                self.log.info('Opped on channel %s on %s', channel, irc.network)
                key = f'{channel}/{irc.network}'
                if key in self.recoveredChannels:
                    self.recoveredChannels.remove(key)
                    self.log.info('Channel %s on %s needs unrecovering')
                    irc.sendMsg(ircmsgs.mode(channel, ('-im')))
            elif mode == '-o' and ircutils.strEqual(arg, irc.nick):
                self.log.info('Deopped on channel %s on %s, requesting op from ChanServ', channel, irc.network)
                irc.sendMsg(self._chanserv(('OP', channel)))

    def doInvite(self, irc, msg):
        '''Invite - see if we're invited by ChanServ and join channel'''
        channel = msg.args[1]
        if not self.registryValue('ChanServ.enable', channel, irc.network):
            return

        if ircutils.strEqual(msg.nick, self.registryValue('ChanServ.nickname')):
            self.log.info('Joining channel %s on %s by invite from ChanServ', channel, irc.network)
            irc.sendMsg(ircmsgs.join(channel))

    def doJoin(self, irc, msg):
        '''Bot joined a channel - request op'''
        channel = msg.channel
        if not self.registryValue('ChanServ.enable', channel, irc.network):
            return

        if ircutils.strEqual(msg.nick, irc.nick):
            self.log.info('Joined channel %s on %s, requesting op from ChanServ', channel, irc.network)
            irc.sendMsg(self._chanserv(('OP', channel)))

    def doNotice(self, irc, msg):
        '''Handle notices from NickServ/ChanServ'''
        nickserv = self.registryValue('NickServ.nickname', network=irc.network)
        chanserv = self.registryValue('ChanServ.nickname', network=irc.network)
        if nickserv and ircutils.strEqual(msg.nick, nickserv):
            self.doNickServNotice(irc, msg)
        elif chanserv and ircutils.strEqual(msg.nick, chanserv):
            self.doChanServNotice(irc, msg)

    def doNickServNotice(self, irc, msg):
        '''Handle notices from NickServ'''

    def doChanServNotice(self, irc, msg):
        '''Handle notices from ChanServ'''
        text = msg.args[1]
        text = ircutils.stripFormatting(text)

        if 'unbanned' in text and 'from' in text:
            matches = search(r'(#[^\s]+)', text)
            if matches:
                channel = matches[1]
                self.log.info('Unbanned from %s on %s by ChanServ, joining', channel, irc.network)
                irc.sendMsg(ircmsgs.join(channel))
        elif 'Channel ' in text and '#' in text and ' key is: ' in text:
            matches = search(r'Channel (#[^\s]+) key is: (.*)', text)
            if matches:
                channel = matches[1]
                key = matches[2]
                self.log.info('Received key for %s on %s from ChanServ, joining', channel, irc.network)
                irc.sendMsg(ircmsgs.join(channel, key=key))

    def _nickserv(self, args=(), prefix='', msg=None):
        '''Construct a NickServ command'''
        if msg and not prefix:
            prefix = msg.prefix

        return ircmsgs.IrcMsg(command='NICKSERV', args=args, prefix=prefix, msg=msg)

    def _chanserv(self, args=(), prefix='', msg=None):
        '''Construct a ChanServ command'''
        if msg and not prefix:
            prefix = msg.prefix

        return ircmsgs.IrcMsg(command='CHANSERV', args=args, prefix=prefix, msg=msg)


Class = Atheme

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
