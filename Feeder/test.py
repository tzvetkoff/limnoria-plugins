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


class FeederTestCase(ChannelPluginTestCase):
    plugins = ('Feeder',)
    config = {}


    def test000CommandFeedAdd(self):
        self.assertRegexp('feeder feed add kernel https://www.kernel.org/feeds/kdist.xml',
                          r'The operation succeeded')
        self.assertRegexp('feeder feed add awesome https://github.com/awesomeWM/awesome/releases.rss',
                          r'The operation succeeded')
        self.assertRegexp('feeder feed add kernel https://www.kernel.org/feeds/kdist.xml',
                          r'Feed kernel already exists')
        self.assertEqual(conf.supybot.plugins.feeder.feeds(), {
            'kernel': {'url': 'https://www.kernel.org/feeds/kdist.xml'},
            'awesome': {'url': 'https://github.com/awesomeWM/awesome/releases.rss'},
        })

    def test001CommandFeedList(self):
        self.assertRegexp('feeder feed list', r'Monitored feeds: kernel')

    def test002CommandFeedRemove(self):
        self.assertRegexp('feeder feed remove foobar', r'Feed foobar not found')
        self.assertRegexp('feeder feed remove awesome', r'The operation succeeded')
        self.assertEqual(conf.supybot.plugins.feeder.feeds(), {
            'kernel': {'url': 'https://www.kernel.org/feeds/kdist.xml'},
        })

    def test003CommandFeedSet(self):
        self.assertRegexp('feeder feed set foobar title FooBar', r'Feed foobar not found')
        self.assertRegexp('feeder feed set foobar k1 v1', r'Metadata k1 not allowed')
        self.assertRegexp('feeder feed set kernel k1 v1', r'Metadata k1 not allowed')
        self.assertRegexp('feeder feed set kernel title Kernel', r'The operation succeeded')
        self.assertEqual(conf.supybot.plugins.feeder.feeds(), {
            'kernel': {'url': 'https://www.kernel.org/feeds/kdist.xml', 'title': 'Kernel'},
        })

    def test004CommandFeedUnset(self):
        self.assertRegexp('feeder feed unset foobar title', r'Feed foobar not found')
        self.assertRegexp('feeder feed unset foobar k1', r'Metadata k1 not allowed')
        self.assertRegexp('feeder feed unset kernel title', r'The operation succeeded')
        self.assertRegexp('feeder feed unset kernel title', r'Feed kernel metadata title not set')
        self.assertEqual(conf.supybot.plugins.feeder.feeds(), {
            'kernel': {'url': 'https://www.kernel.org/feeds/kdist.xml'},
        })

    def test010CommandAnnounceAdd(self):
        self.assertRegexp('feeder announce add #channel foobar', r'Channel #channel not found')
        self.assertRegexp('feeder announce add #test foobar', r'Feed foobar not found')
        self.assertRegexp('feeder announce add #test kernel', r'The operation succeeded')
        self.assertEqual(conf.supybot.plugins.feeder.announces.getSpecific(network='test')(), {
            '#test': ['kernel'],
        })

    def test011CommandAnnounceList(self):
        self.assertRegexp('feeder announce list', r'{\'#test\': \[\'kernel\'\]}')

    def test012CommandAnnounceReset(self):
        self.assertRegexp('feeder announce reset #channel foobar', r'Channel #channel not found')
        self.assertRegexp('feeder announce reset #test foobar', r'Feed foobar not found')
        self.assertRegexp('feeder announce reset #test kernel', r'The operation succeeded')
        self.assertEqual(conf.supybot.plugins.feeder.announces.getSpecific(network='test')(), {
            '#test': ['kernel'],
        })

    def test013CommandAnnounceRemove(self):
        self.assertRegexp('feeder announce remove #channel foobar', r'Channel #channel not found')
        self.assertRegexp('feeder announce remove #test foobar', r'Feed foobar not found')
        self.assertRegexp('feeder announce remove #test kernel', r'The operation succeeded')
        self.assertEqual(conf.supybot.plugins.feeder.announces.getSpecific(network='test')(), {})


    def dbg(self, msg):
        print()
        print('-*'*32, '-', sep='')
        print(msg)
        print('-*'*32, '-', sep='')
        print()

    def cmd(self, cmd, *_args, **_kvargs):
        self.dbg(self.getMsg(cmd))

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
