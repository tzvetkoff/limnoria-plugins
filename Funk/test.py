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
# pylint:disable=missing-class-docstring
# pylint:disable=missing-function-docstring
# pylint:disable=wildcard-import
# pylint:disable=unused-wildcard-import
# pylint:disable=redefined-builtin

from supybot.test import *


class FunkTestCase(PluginTestCase):
    plugins = ('Funk',)

    def testFunkRot13(self):
        self.assertRegexp('rot13 the quick brown fox jumps over the lazy dog',
                          r'gur dhvpx oebja sbk whzcf bire gur ynml qbt')
        self.assertRegexp('rot13 The Quick Brown Fox Jumps Over The Lazy Dog',
                          r'Gur Dhvpx Oebja Sbk Whzcf Bire Gur Ynml Qbt')

    def testFunkUnrot13(self):
        self.assertRegexp('unrot13 gur dhvpx oebja sbk whzcf bire gur ynml qbt',
                          r'the quick brown fox jumps over the lazy dog')
        self.assertRegexp('unrot13 Gur Dhvpx Oebja Sbk Whzcf Bire Gur Ynml Qbt',
                          r'The Quick Brown Fox Jumps Over The Lazy Dog')

    def testFunkPig(self):
        self.assertRegexp('pig nix', r'ixnay')
        self.assertRegexp('pig Nix', r'Ixnay')
        self.assertRegexp('pig ork', r'orkyay')
        self.assertRegexp('pig Ork', r'Orkyay')
        self.assertRegexp('pig oyster', r'oysteryay')
        self.assertRegexp('pig Oyster', r'oysteryay')
        self.assertRegexp('pig ophthalmology', r'ophthalmologyyay')
        self.assertRegexp('pig Ophthalmology', r'Ophthalmologyyay')
        self.assertRegexp('pig the quick brown fox jumps over the lazy dog',
                          r'hetay uickqay rownbay oxfay umpsjay overyay hetay azylay ogday')
        self.assertRegexp('pig The Quick Brown Fox Jumps Over The Lazy Dog',
                          r'Hetay Uickqay Rownbay Oxfay Umpsjay Overyay Hetay Azylay Ogday')

    def testFunkUnpig(self):
        self.assertRegexp('unpig ixnay', r'nix')
        self.assertRegexp('unpig Ixnay', r'Nix')
        self.assertRegexp('unpig orkyay', r'ork')
        self.assertRegexp('unpig Orkyay', r'Ork')
        self.assertRegexp('unpig oysteryay', r'oyster')
        self.assertRegexp('unpig oysteryay', r'Oyster')
        self.assertRegexp('unpig ophthalmologyyay', r'ophthalmology')
        self.assertRegexp('unpig Ophthalmologyyay', r'Ophthalmology')
        self.assertRegexp('unpig hetay uickqay rownbay oxfay umpsjay overyay hetay azylay ogday',
                          r'the quick brown fox jumps over the lazy dog')
        self.assertRegexp('unpig Hetay Uickqay Rownbay Oxfay Umpsjay Overyay Hetay Azylay Ogday',
                          r'The Quick Brown Fox Jumps Over The Lazy Dog')

    def testRoman(self):
        self.assertRegexp('roman 666', r'666 => DCLXVI')
        self.assertRegexp('roman DCLXVI', r'DCLXVI => 666')
        self.assertRegexp('roman dclxvi', r'DCLXVI => 666')
        self.assertRegexp('roman dcl1xvi', r'Input "dcl1xvi" is invalid!')
        self.assertRegexp('roman 0', r'Input "0" is invalid!')
        self.assertRegexp('roman 4000', r'Input "4000" is invalid!')

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
