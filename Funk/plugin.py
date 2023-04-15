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

from supybot import callbacks
from supybot.commands import wrap
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Funk')
except ImportError:
    def _(x):
        return x

import codecs
import random
import os
import re


class Funk(callbacks.Plugin):
    '''A collection of useless fun commands'''
    threaded = True

    def _randline(self, fn):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', fn)) as fh:
            return random.sample(fh.read().splitlines(), 1)[0]

    @wrap
    def bofh(self, irc, msg, args):
        '''BOFH (Bastard Operator From Hell) excuse generator
        '''
        irc.reply(self._randline('bofh.txt'), prefixNick=self.registryValue('prefixNick', msg.channel, irc.network))

    @wrap
    def chuck(self, irc, msg, args):
        '''Tells a Chuck Norris joke
        '''
        irc.reply(self._randline('chuck.txt'), prefixNick=self.registryValue('prefixNick', msg.channel, irc.network))

    @wrap([
        'text',
    ])
    def rot13(self, irc, msg, args, text):
        '''<text>
        Encode text with ROT13
        '''
        irc.reply(codecs.encode(text, 'rot_13'), prefixNick=self.registryValue('prefixNick', msg.channel, irc.network))

    @wrap([
        'text',
    ])
    def unrot13(self, irc, msg, args, text):
        '''<text>
        Decode ROT13 text
        '''
        irc.reply(codecs.decode(text, 'rot_13'), prefixNick=self.registryValue('prefixNick', msg.channel, irc.network))

    def _pigword(self, word):
        capital = word[:1] == word[:1].upper()
        word = word.lower()
        letters = 'qwertyuiopasdfghjklzxcvbnm'
        i = len(word) - 1
        while i >= 0 and letters.find(word[i]) == -1:
            i = i - 1
        if i == -1:
            return word
        punctuation = word[i + 1:]
        word = word[: i + 1]

        vowels = 'aeiou'
        if word[0] in vowels:
            word = word + 'yay' + punctuation
        else:
            word = word[1:] + word[0] + 'ay' + punctuation

        if capital:
            return word[:1].upper() + word[1:]
        else:
            return word

    def _unpigword(self, word):
        capital = False
        word = word.lower()
        letters = 'qwertyuiopasdfghjklzxcvbnm'
        i = len(word) - 1
        while i >= 0 and letters.find(word[i]) == -1:
            i = i - 1
        if i == -1:
            return word
        punctuation = word[i + 1:]
        word = word[: i + 1]

        vowels = 'aeiou'
        if word[0] in vowels and word.endswith('yay'):
            word = word[:-3] + punctuation
        elif word.endswith('ay'):
            word = word[-3] + word[:-3] + punctuation
        else:
            word = word + punctuation

        if capital:
            return word[:1].upper() + word[1:]
        else:
            return word

    @wrap([
        'text',
    ])
    def pig(self, irc, msg, args, text):
        '''<text>
        Convert text from English to Pig Latin.
        '''
        words = re.split(r'\s+', text)
        words = [self._pigword(word) for word in words]
        irc.reply(' '.join(words), prefixNick=self.registryValue('prefixNick', msg.channel, irc.network))

    @wrap([
        'text'
    ])
    def unpig(self, irc, msg, args, text):
        '''<text>
        Convert text from Pig Latin to English.
        '''
        words = re.split(r'\s+', text)
        words = [self._unpigword(word) for word in words]
        irc.reply(' '.join(words), prefixNick=self.registryValue('prefixNick', msg.channel, irc.network))


Class = Funk

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
