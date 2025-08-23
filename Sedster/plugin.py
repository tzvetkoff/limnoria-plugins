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
# pylint:disable=missing-class-docstring
# pylint:disable=missing-function-docstring
# pylint:disable=wrong-import-order
# pylint:disable=broad-exception-caught
# pylint:disable=too-many-ancestors
# pylint:disable=too-many-branches
# pylint:disable=too-many-arguments
# pylint:disable=inconsistent-return-statements
# pyright:reportImplicitStringConcatenation=none

from supybot import callbacks, ircdb, ircmsgs, ircutils, utils
from supybot.commands import ProcessTimeoutError, process
import re

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Sedster')
except ImportError:
    def _(x):
        return x

# The regular expression that the plugin will react on.
SEDSTER_REGEXP = re.compile(
    # Match and save the delimiter (any one symbol) as a named group
    r'^s(?P<delim>[^\w\s])'

    # Match the pattern to replace, which can be any string up to the first instance of the delimiter
    r'(?P<pattern>(?:(?!(?P=delim)).)*)(?P=delim)'

    # Ditto with the replacement
    r'(?P<replacement>(?:(?!(?P=delim)).)*)'

    # Optional final delimiter plus flags at the end and/or replacement index
    r'(?:(?P=delim)(?P<flags>[0-9a-z]*))?'
)

# Replace newlines and friends with things like literal '\n'
WHITESPACE_REPLACER = utils.str.MultipleReplacer({
    '\n': '\\n',
    '\t': '\\t',
    '\r': '\\r',
})


class SearchNotFoundError(Exception):
    pass


class Sedster(callbacks.PluginRegexp):
    '''
    Enable Sedster on the desired channels:
    `config channel #yourchannel plugins.sedster.enable True`
    After enabling Sedster, typing a regex in the form
    `s/text/replacement/` will make the bot announce replacements.

    ::
        20:24 <Polizei> helli wirld
        20:24 <Polizei> s/i/o/
        20:24 <Limnoria> <Polizei> hello wirld
        20:24 <Polizei> s/i/o/g
        20:24 <Limnoria> <Polizei> hello world
        20:24 <Polizei> s/i/o/2
        20:24 <Limnoria> <Polizei> helli world

    The following regex flags (i.e. the `g` in `s/abc/def/g`, etc.) are supported:

    - `i`: case insensitive replacement
    - `g`: replace all occurences of the original text
    - `NUMBER`: replace the nth occurence, e.g. `s/foo/bar/2` will replace only the 2nd
    '''

    threaded = True

    flags = 0   # Make callback matching case sensitive
    unaddressedRegexps = ['sedster_hook']

    def _parse_regexp(self, expr):
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

        match = SEDSTER_REGEXP.search(escaped_expr)

        if not match:
            raise ValueError('Invalid expression')

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
                count = count * 10 + int(flag)

        if count is None:
            count = 1

        pattern = re.compile(pattern, flags)

        return pattern, replacement, count, raw_flags

    # Sedster main routine.
    # This is called automatically by callbacks.PluginRegexp on every message that matches the SEDSTER_REGEXP regexp.
    # The actual regexp is passed into PluginRegexp by setting `__doc__` on the hook method.
    def sedster_hook(self, irc, msg, _regex):
        if not self.registryValue('enable', msg.channel, irc.network):
            return

        try:
            pattern, replacement, count, _flags = self._parse_regexp(msg.args[1])
        except Exception as e:
            self.log.error(_('Sedster :: %s: %s'), str(type(e)), e, exc_info=True)

            if self.registryValue('displayErrors', msg.channel, irc.network):
                errmsg = f'{e.__class__.__module__}:{e.__class__.__name__}: {e}'
                irc.error(errmsg)

            return

        history = reversed(irc.state.history)
        timeout = self.registryValue('processTimeout')

        try:
            message = process(
                self._sedster_process,
                irc,
                msg,
                pattern,
                replacement,
                count,
                history,
                timeout=timeout,
                pn=self.name(),
                cn='replacer',
            )
        except ProcessTimeoutError as e:
            errmsg = _('Sedster :: Search timed out')
            self.log.error(errmsg, e, exc_info=True)

            if self.registryValue('displayErrors', msg.channel, irc.network):
                irc.error(errmsg)
        except SearchNotFoundError as e:
            errmsg = _('Sedster :: Search not found in the last %i IRC messages on this network') % (len(irc.state.history))
            self.log.error(errmsg, e, exc_info=True)

            if self.registryValue('displayErrors', msg.channel, irc.network):
                irc.error(errmsg)
        except Exception as e:
            errmsg = f'Sedster :: {e.__class__.__module__}:{e.__class__.__name__}: {e}'
            self.log.error(errmsg, e, exc_info=True)

            if self.registryValue('displayErrors', msg.channel, irc.network):
                irc.error(errmsg)
        else:
            irc.reply(message, prefixNick=False)

    # Set the regexp so PluginRegexp knows how to handle it.
    sedster_hook.__doc__ = SEDSTER_REGEXP.pattern

    # Regular expression process callback.
    # We run it in a subprocess so we can safely isolate it from the main process, and so we can also apply
    # time constraints.
    def _sedster_process(self, irc, msg, pattern, replacement, count, messages):
        for m in messages:
            if m.command != 'PRIVMSG':
                continue
            if ircmsgs.isAction(m):
                continue
            if not ircutils.strEqual(m.args[0], msg.args[0]):
                continue
            if not m.tagged('receivedBy') == irc:
                continue
            if not ircutils.strEqual(m.nick, msg.nick):
                continue
            if ircdb.checkIgnored(m.prefix):
                continue

            # Ignore messages containing a regexp if ignoreRegexps is on.
            if self.registryValue('ignoreRegexps', msg.channel, irc.network) and SEDSTER_REGEXP.match(m.args[1]):
                self.log.debug(_('Sedster :: Skipping message %s because it is tagged as isRegex'), m.args[1])
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

                    subst = WHITESPACE_REPLACER(subst)

                    return _('<%s> %s') % (msg.nick, subst)
            except Exception as e:
                self.log.warning(_('Sedster :: %s: %s'), str(type(e)), e, exc_info=True)
                raise

        self.log.debug(
            _('Sedster :: Search %r not found in the last %i messages of %s'),
            msg.args[1],
            len(irc.state.history),
            msg.args[0],
        )
        raise SearchNotFoundError()


Class = Sedster

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
