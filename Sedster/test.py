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
# pylint:disable=wildcard-import
# pylint:disable=unused-wildcard-import
# pylint:disable=redefined-builtin

import unittest
from supybot.test import *


class SedsterTestCase(ChannelPluginTestCase):
    other = 'blah!blah@someone.else'
    other2 = 'ghost!ghost@spooky'

    plugins = ('Sedster', 'Utilities')
    config = {'plugins.sedster.enable': True,
              'plugins.sedster.boldReplacementText': False,
              'plugins.sedster.displayErrors': True}

    # getMsg() stalls if no message is ever sent (i.e. if the plugin fails to respond to a request)
    # We should limit the timeout to prevent the tests from taking forever.
    timeout = 1

    def testSimpleReplace(self):
        self.feedMsg('Abcd abcdefgh')
        self.feedMsg('s/abcd/test/')
        # Run an empty command so that messages from the previous trigger are caught.
        m = self.getMsg(' ')
        self.assertIn('Abcd testefgh', str(m))

    def testNoMatch(self):
        self.feedMsg('hello world')
        self.feedMsg('s/goodbye//')
        m = self.getMsg(' ')
        self.assertIn('Search not found', str(m))
        self.feedMsg('s/Hello/hi/')  # wrong case
        m = self.getMsg(' ')
        self.assertIn('Search not found', str(m))

    def testCaseInsensitiveReplace(self):
        self.feedMsg('Aliens Are Invading, Help!')
        self.feedMsg('s/a/e/i')
        m = self.getMsg(' ')
        self.assertIn('eliens', str(m))

    def testIgnoreRegexWithBadCase(self):
        self.feedMsg('aliens are invading, help!')
        self.assertSnarfNoResponse('S/aliens/monsters/')

    def testGlobalReplace(self):
        self.feedMsg('AAaa aaAa a b')
        self.feedMsg('s/a/e/g')
        m = self.getMsg(' ')
        self.assertIn('AAee eeAe e b', str(m))

    def testGlobalCaseInsensitiveReplace(self):
        self.feedMsg('Abba')
        self.feedMsg('s/a/e/gi')
        m = self.getMsg(' ')
        self.assertIn('ebbe', str(m))

    def testOnlySelfReplace(self):
        self.feedMsg('evil machines')
        self.feedMsg('evil tacocats', frm=self.__class__.other)
        self.feedMsg('s/evil/kind/s')
        m = self.getMsg(' ')
        self.assertIn('kind machines', str(m))

    def testAllFlagsReplace(self):
        self.feedMsg('Terrible, terrible crimes')
        self.feedMsg('Terrible, terrible TV shows', frm=self.__class__.other)
        self.feedMsg('s/terr/horr/sgi')
        m = self.getMsg(' ')
        self.assertIn('horrible, horrible crimes', str(m))

    def testBoldReplacement(self):
        with conf.supybot.plugins.sedster.boldReplacementText.context(True):
            self.feedMsg('hahahaha', frm=self.__class__.other)

            # One replacement
            self.feedMsg('s/h/H/', frm=self.__class__.other)
            m = self.getMsg(' ')
            self.assertIn('\x02H\x02aha', str(m))

            # Replace all instances
            self.feedMsg('s/h/H/g', frm=self.__class__.other)
            m = self.getMsg(' ')
            self.assertIn('\x02H\x02a\x02H\x02a', str(m))

            # One whole word
            self.feedMsg('sweet dreams are made of this', frm=self.__class__.other)
            self.feedMsg('s/this/cheese/', frm=self.__class__.other)
            m = self.getMsg(' ')
            self.assertIn('of \x02cheese\x02', str(m))

    def testNonSlashSeparator(self):
        self.feedMsg('we are all decelopers on this blessed day')
        self.feedMsg('s.c.v.')
        m = self.getMsg(' ')
        self.assertIn('developers', str(m))

        self.feedMsg('4 / 2 = 8')
        self.feedMsg('s@/@*@')
        m = self.getMsg(' ')
        self.assertIn('4 * 2 = 8', str(m))

    def testWeirdSeparatorsFail(self):
        self.feedMsg('can\'t touch this', frm=self.__class__.other)
        # Only symbols are allowed as separators
        self.feedMsg('blah: s a b ')
        self.feedMsg('blah: sdadbd')

        self.getMsg('echo dummy message')

        # XXX: this is a total hack...
        for msg in self.irc.state.history:
            self.assertNotIn('cbn\'t', str(msg))

    # https://github.com/jlu5/SupyPlugins/commit/e19abe049888667c3d0a4eb4a2c3ae88b8bea511
    # We want to make sure the bot treats channel names case-insensitively, if some client
    # writes to it using a differente case.
    def testCaseNormalizationInRead(self):
        assert self.channel != self.channel.title()  # In case Limnoria's defaults change
        self.feedMsg('what a strange bug', to=self.channel.title())
        self.feedMsg('s/strange/hilarious/', to=self.channel)
        m = self.getMsg(' ')
        self.assertIn('what a hilarious bug', str(m))

    def testCaseNormalizationInReplace(self):
        assert self.channel != self.channel.title()  # In case Limnoria's defaults change
        self.feedMsg('Segmentation fault', to=self.channel)
        self.feedMsg('s/$/ (core dumped)/', to=self.channel.title())
        m = self.getMsg(' ')
        self.assertIn('Segmentation fault (core dumped)', str(m))

    @unittest.skipIf(world.disableMultiprocessing, 'Test requires multiprocessing to be enabled')
    def testReDoSTimeout(self):
        # From https://snyk.io/blog/redos-and-catastrophic-backtracking/
        for _ in range(500):
            self.feedMsg('ACCCCCCCCCCCCCCCCCCCCCCCCCCCCX')
        self.feedMsg(r's/A(B|C+)+D/this should abort/')
        m = self.getMsg(' ', timeout=1)
        self.assertIn('timed out', str(m))

    def testMissingTrailingSeparator(self):
        # Allow the plugin to work if you miss the trailing /
        self.feedMsg('hello world')
        self.feedMsg('s/world/everyone')
        m = self.getMsg(' ')
        self.assertIn('hello everyone', str(m))

        # Make sure it works if there's a space in the replacement
        self.feedMsg('hello world')
        self.feedMsg('s@world@how are you')
        m = self.getMsg(' ')
        self.assertIn('hello how are you', str(m))

        # Ditto with a space in the original text
        self.feedMsg('foo bar @ baz')
        self.feedMsg('s/bar @/and')
        m = self.getMsg(' ')
        self.assertIn('foo and baz', str(m))

    def testIgnoreTextAfterTrailingSeparator(self):
        # https://github.com/jlu5/SupyPlugins/issues/59
        self.feedMsg('see you ltaer')
        self.feedMsg('s/ltaer/later/ this text will be ignored')
        m = self.getMsg(' ')
        self.assertIn('see you later', str(m))

        self.feedMsg('s/LTAER/later, bye/i <extra text>')
        m = self.getMsg(' ')
        self.assertIn('see you later, bye', str(m))

    def testIgnoreRegexOnMessagesBeforeEnable(self):
        # Before 2020-10-12 Sedster used a single msg.tag() to track and ignore messages parsed as a regexp.
        # However, a common complaint is that this doesn't catch regexps sent before Sedster was loaded/enabled...
        with conf.supybot.plugins.sedster.enable.context(False):
            self.feedMsg('foo')
            self.feedMsg('barbell')
            self.feedMsg('s/foo/bar/')
            self.feedMsg('abcdef')
        self.feedMsg('s/bar/door/')
        m = self.getMsg(' ')
        # The INCORRECT response would be 's/foo/door/'
        self.assertIn('doorbell', str(m))

    def testPositionalReplace(self):
        self.feedMsg('see you later, alligater')
        self.feedMsg('s/ter/tor/2')
        m = self.getMsg(' ')
        self.assertIn('see you later, alligator', str(m))

    # TODO: test ignores

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
