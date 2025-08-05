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

from supybot.test import *
from supybot import world


class FeederTestCase(ChannelPluginTestCase):
    plugins = ('Feeder',)
    config = {}

    def test000CommandFeedsAlias(self):
        self.assertRegexp('feeder feed list', r'No feeds configured')

    def test001CommandFeedsAdd(self):
        self.assertRegexp('feeder feeds add kernel https://www.kernel.org/feeds/kdist.xml',
                          r'The operation succeeded')
        self.assertRegexp('feeder feeds add awesome https://github.com/awesomeWM/awesome/releases.rss',
                          r'The operation succeeded')
        self.assertRegexp('feeder feeds add kernel https://www.kernel.org/feeds/kdist.xml',
                          r'Feed kernel already exists')
        self.assertEqual(conf.supybot.plugins.feeder.feeds(), {
            'kernel': {'url': 'https://www.kernel.org/feeds/kdist.xml'},
            'awesome': {'url': 'https://github.com/awesomeWM/awesome/releases.rss'},
        })

    def test002CommandFeedsList(self):
        self.assertRegexp('feeder feeds list', r'kernel')

    def test003CommandFeedsInfo(self):
        self.assertRegexp('feeder feeds info foobar', r'Feed foobar not found')
        self.assertRegexp('feeder feeds info kernel', r'{"url":"https://www.kernel.org/feeds/kdist.xml"}')

    def test004CommandFeedsRemove(self):
        self.assertRegexp('feeder feeds remove foobar', r'Feed foobar not found')
        self.assertRegexp('feeder feeds remove awesome', r'The operation succeeded')
        self.assertEqual(conf.supybot.plugins.feeder.feeds(), {
            'kernel': {'url': 'https://www.kernel.org/feeds/kdist.xml'},
        })

    def test005CommandFeedsSet(self):
        self.assertRegexp('feeder feeds set foobar title FooBar', r'Feed foobar not found')
        self.assertRegexp('feeder feeds set foobar k1 v1', r'Metadata k1 not allowed')
        self.assertRegexp('feeder feeds set kernel k1 v1', r'Metadata k1 not allowed')
        self.assertRegexp('feeder feeds set kernel title Kernel', r'The operation succeeded')
        self.assertEqual(conf.supybot.plugins.feeder.feeds(), {
            'kernel': {'url': 'https://www.kernel.org/feeds/kdist.xml', 'title': 'Kernel'},
        })

    def test006CommandFeedsUnset(self):
        self.assertRegexp('feeder feeds unset foobar title', r'Feed foobar not found')
        self.assertRegexp('feeder feeds unset foobar k1', r'Metadata k1 not allowed')
        self.assertRegexp('feeder feeds unset kernel title', r'The operation succeeded')
        self.assertRegexp('feeder feeds unset kernel title', r'Feed kernel metadata title not set')
        self.assertEqual(conf.supybot.plugins.feeder.feeds(), {
            'kernel': {'url': 'https://www.kernel.org/feeds/kdist.xml'},
        })

    def test010CommandAnnouncesAlias(self):
        self.assertRegexp('feeder announce list', r'No announces configured')

    def test011CommandAnnouncesAdd(self):
        self.assertRegexp('feeder announces add #channel foobar', r'Channel #channel not found')
        self.assertRegexp('feeder announces add #test foobar', r'Feed foobar not found')
        self.assertRegexp('feeder announces add #test kernel', r'The operation succeeded')
        self.assertEqual(conf.supybot.plugins.feeder.announces.getSpecific(network='test')(), {
            '#test': ['kernel'],
        })

    def test012CommandAnnouncesList(self):
        self.assertRegexp('feeder announces list', r'{"#test":\["kernel"\]}')

    def test013CommandAnnouncesReset(self):
        self.assertRegexp('feeder announces reset #channel foobar', r'Channel #channel not found')
        self.assertRegexp('feeder announces reset #test foobar', r'Feed foobar not found')
        self.assertRegexp('feeder announces reset #test kernel', r'The operation succeeded')
        self.assertEqual(conf.supybot.plugins.feeder.announces.getSpecific(network='test')(), {
            '#test': ['kernel'],
        })

    def test014CommandAnnouncesRemove(self):
        self.assertRegexp('feeder announces remove #channel foobar', r'Channel #channel not found')
        self.assertRegexp('feeder announces remove #test foobar', r'Feed foobar not found')
        self.assertRegexp('feeder announces remove #test kernel', r'The operation succeeded')
        self.assertEqual(conf.supybot.plugins.feeder.announces.getSpecific(network='test')(), {})

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
