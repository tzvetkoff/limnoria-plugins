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

from supybot.commands import *
from supybot.commands import ProcessTimeoutError
import supybot.plugins as plugins
import supybot.ircmsgs as ircmsgs
import supybot.callbacks as callbacks
import supybot.ircutils as ircutils
import supybot.ircdb as ircdb
import supybot.utils as utils

import re
import sys

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Sedster')
except ImportError:
    _ = lambda x: x

TAG_SEEN = 'Sedster.seen'
TAG_IS_REGEX = 'Stdster.isRegex'

SED_REGEX = re.compile(
    # Match and save the delimiter (any one symbol) as a named group
    r'^s(?P<delim>[^\w\s])'

    # Match the pattern to replace, which can be any string up to the first instance of the delimiter
    r'(?P<pattern>(?:(?!(?P=delim)).)*)(?P=delim)'

    # Ditto with the replacement
    r'(?P<replacement>(?:(?!(?P=delim)).)*)'

    # Optional final delimiter plus flags at the end and/or replacement index
    r'(?:(?P=delim)(?P<flags>[0-9a-z]*))?'
)

# Replace newlines and friends with things like literal '\n' (backslash and 'n')
axe_spaces = utils.str.MultipleReplacer({'\n': '\\n', '\t': '\\t', '\r': '\\r'})

class SearchNotFoundError(Exception):
    pass

class Sedster(callbacks.PluginRegexp):
    '''
    Enable Sedster on the desired channels:
    ``config channel #yourchannel plugins.sedster.enable True``
    After enabling Sedster, typing a regex in the form
    ``s/text/replacement/`` will make the bot announce replacements.

    ::

       20:24 <Polizei> helli wirld
       20:24 <Polizei> s/i/o/
       20:24 <Limnoria> <Polizei> hello wirld
       20:24 <Polizei> s/i/o/g
       20:24 <Limnoria> <Polizei> hello world
       20:24 <Polizei> s/i/o/2
       20:24 <Limnoria> <Polizei> helli world

    You can also do ``othernick: s/text/replacement/`` to only replace
    messages from a certain user. Supybot ignores are respected by the plugin,
    and messages from ignored users will only be considered if their nick is
    explicitly given.

    Regex flags
    ^^^^^^^^^^^

    The following regex flags (i.e. the ``g`` in ``s/abc/def/g``, etc.) are supported:

    - ``i``: case insensitive replacement
    - ``g``: replace all occurences of the original text
    '''

    threaded = True
    public = True
    unaddressedRegexps = ['replacer']
    flags = 0  # Make callback matching case sensitive

    @staticmethod
    def _unpack_sed(expr):
        if '\0' in expr:
            raise ValueError('Expression can\'t contain NUL')

        delim = expr[1]
        escaped_expr = ''

        for (i, c) in enumerate(expr):
            if c == delim and i > 0:
                if expr[i - 1] == '\\':
                    escaped_expr = escaped_expr[:-1] + '\0'
                    continue

            escaped_expr += c

        match = SED_REGEX.search(escaped_expr)

        if not match:
            return

        groups = match.groupdict()
        pattern = groups['pattern'].replace('\0', delim)
        replacement = groups['replacement'].replace('\0', delim)

        if groups['flags']:
            raw_flags = set(groups['flags'])
        else:
            raw_flags = set()

        flags = 0
        count = None

        for flag in raw_flags:
            if flag == 'g':
                count = 0
            elif flag == 'i':
                flags |= re.IGNORECASE
            elif flag in '0123456789':
                if count is None:
                    count = 0
                count = count*10 + int(flag)

        if count is None:
            count = 1

        pattern = re.compile(pattern, flags)

        return (pattern, replacement, count, raw_flags)

    # Tag all messages that Sedster has seen before. This slightly optimizes the ignoreRegex
    # feature as all messages tagged with Sedster.seen but not Sedster.isRegex is NOT a regexp.
    # If we didn't have this tag, we'd have to run a regexp match on each message in the history
    # to check if it's a regexp, as there could've been regexp-like messages sent before
    # Sedster was enabled.
    def doNotice(self, irc, msg):
        if self.registryValue('enable', msg.channel, irc.network):
            msg.tag(TAG_SEEN)

    def doPrivmsg(self, irc, msg):
       # callbacks.PluginRegexp works by defining doPrivmsg(), we don't want to overwrite
       # its behaviour
       super().doPrivmsg(irc, msg)
       self.doNotice(irc, msg)

    # Sedster main routine. This is called automatically by callbacks.PluginRegexp on every
    # message that matches the SED_REGEX expression defined in constants.py
    # The actual regexp is passed into PluginRegexp by setting __doc__ equal to the regexp.
    def replacer(self, irc, msg, regex):
        if not self.registryValue('enable', msg.channel, irc.network):
            return

        self.log.debug(_('Sedster: running on %s/%s for %s'), irc.network, msg.channel, regex)
        iterable = reversed(irc.state.history)
        msg.tag(TAG_IS_REGEX)

        try:
            (pattern, replacement, count, flags) = self._unpack_sed(msg.args[1])
        except Exception as e:
            self.log.warning(_('Sedster parser error: %s'), e, exc_info=True)
            if self.registryValue('displayErrors', msg.channel, irc.network):
                irc.error('%s.%s: %s' % (e.__class__.__module__, e.__class__.__name__, e))
            return

        regex_timeout = self.registryValue('processTimeout')
        try:
            message = process(self._replacer_process, irc, msg, pattern, replacement, count, iterable,
                    timeout=regex_timeout, pn=self.name(), cn='replacer')
        except ProcessTimeoutError:
            irc.error(_('Search timed out.'))
        except SearchNotFoundError:
            irc.error(_('Search not found in the last %i IRC messages on this network.') % len(irc.state.history))
        except Exception as e:
            self.log.warning(_('Sedster replacer error: %s'), e, exc_info=True)
            if self.registryValue('displayErrors', msg.channel, irc.network):
                irc.error('%s.%s: %s' % (e.__class__.__module__, e.__class__.__name__, e))
        else:
            irc.reply(message, prefixNick=False)
    replacer.__doc__ = SED_REGEX.pattern

    def _replacer_process(self, irc, msg, pattern, replacement, count, messages):
        for m in messages:
            if m.command in ('PRIVMSG') and ircutils.strEqual(m.args[0], msg.args[0]) and m.tagged('receivedBy') == irc:
                # Don't do actions.
                if ircmsgs.isAction(m):
                    continue

                # Skip if message is from different sender.
                if m.nick != msg.nick:
                    continue

                # Don't snarf ignored users' messages unless specifically told to.
                if ircdb.checkIgnored(m.prefix):
                    continue

                # Test messages sent before Sedster was activated.
                # Mark them all as seen so we only need to do this check once per message.
                if not m.tagged(TAG_SEEN):
                    m.tag(TAG_SEEN)
                    if SED_REGEX.match(m.args[1]):
                        m.tag(TAG_IS_REGEX)

                # Ignore messages containing a regexp if ignoreRegex is on.
                if self.registryValue('ignoreRegex', msg.channel, irc.network) and m.tagged(TAG_IS_REGEX):
                    self.log.debug(_('Skipping message %s because it is tagged as isRegex'), m.args[1])
                    continue

                # Do the replacements.
                text = m.args[1]
                try:
                    replace_result = pattern.search(text)
                    if replace_result:
                        if self.registryValue('boldReplacementText', msg.channel, irc.network):
                            replacement = ircutils.bold(replacement)

                        if count == 0:
                            subst = pattern.sub(replacement, text, count)
                        else:
                            position = [(match.start(), match.end()) for match in pattern.finditer(text)][count - 1]
                            subst = text[:position[0]] + replacement + text[position[1]:]

                        subst = axe_spaces(subst)

                        return _('<%s> %s') % (msg.nick, subst)
                except Exception as e:
                    self.log.warning(_('Sedster error: %s'), e, exc_info=True)
                    raise

        self.log.debug(_('Sedster: Search %r not found in the last %i messages of %s.'),
                msg.args[1], len(irc.state.history), msg.args[0])
        raise SearchNotFoundError()

Class = Sedster

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
