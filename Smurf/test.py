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
# pylint:disable=line-too-long

from supybot.test import *


class SmurfTestCase(ChannelPluginTestCase):
    plugins = ('Smurf',)
    config = {
        'plugins.smurf.enable': True,
        'plugins.smurf.timeout': 3.5,
        'plugins.smurf.reportErrors': True,
        'plugins.smurf.smurfMultipleURLs': True,
        # 'plugins.smurf.ignoreUrlRegexp': '/porn/',
        # 'plugins.smurf.ignoreDomains': 'pfoo.org'
    }
    timeout = 5

    @unittest.skipUnless(network, 'smurf tests require networking')
    def testSmurf000Normal(self):
        self.assertRegexp('smurf https://pfoo.org/', r'^>> pfoo! \(at pfoo.org\)$')

    @unittest.skipUnless(network, 'smurf tests require networking')
    def testSmurf001ChannelMessageNormal(self):
        self.assertSnarfResponse('https://pfoo.org/,', '>> pfoo! (at pfoo.org)')

    @unittest.skipUnless(network, 'smurf tests require networking')
    def testSmurf002ChannelMessageIgnoreUrlRegexp(self):
        ignore_url_regexp_var = conf.supybot.plugins.smurf.ignoreUrlRegexp

        try:
            self.timeout = 1
            ignore_url_regexp_var.set(r'/porn/')
            self.assertSnarfNoResponse('https://pfoo.org/the-internet-is-for-porn/')
        finally:
            self.timeout = 5
            ignore_url_regexp_var.set(None)

    @unittest.skipUnless(network, 'smurf tests require networking')
    def testSmurf003ChannelMessageIgnoreDomains(self):
        ignore_domains = conf.supybot.plugins.smurf.ignoreDomains

        try:
            self.timeout = 1
            ignore_domains.set('pfoo.org')
            self.assertSnarfNoResponse('https://pfoo.org/')
        finally:
            self.timeout = 5
            ignore_domains.set('')

    @unittest.skipUnless(network, 'smurf tests require networking')
    def testSmurf004Twitter(self):
        self.assertSnarfResponse('https://x.com/QuotesFuturama/status/1825513336236109929', '>> Futurama Quotes (@QuotesFuturama) on X: Marquita Maria Christina Chiquita Alana Paloma Ramona Rosita Catalina Lupe Martes Miercoles Jueves Viernes Sabado Domingo Veronica Helena Hermina Francesca Esperanza Valentina Carmelita Leonora Lupita Isabella Juanita Teresa Sofia Mariana Benihana Bonita Nereida Guadalupe Alvarez  pic.twitter.com/CnqpQslRoB [August 19, 2024] (at x.com)')

    @unittest.skipUnless(network, 'smurf tests require networking')
    def testSmurf005YouTube(self):
        self.assertSnarfResponse('https://www.youtube.com/watch?v=cJygmsFYf9w', '>> Patlamaya Devam - Isyan Tetick - 1 Hour Alien Video - with english lyrics - ИНОПЛАНЕТЯНИН (at www.youtube.com)')

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
