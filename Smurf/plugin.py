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

# pylama:ignore=C901

from html.entities import entitydefs
from urllib.parse import urlunparse
import re
import requests
from time import time
from supybot import conf, utils, ircmsgs, callbacks
from supybot.commands import wrap

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Smurf')
except ImportError:
    def _(x):
        return x


class Smurf(callbacks.Plugin):
    '''Fetches URL titles'''
    threaded = True

    def doPrivmsg(self, irc, msg):
        if not msg.channel:
            return
        if not self.registryValue('enable', msg.channel, irc.network):
            return
        if ircmsgs.isCtcp(msg) and not ircmsgs.isAction(msg):
            return

        if ircmsgs.isAction(msg):
            text = ircmsgs.unAction(msg)
        else:
            text = msg.args[1]

        ignoreUrlRe = self.registryValue('ignoreUrlRegexp', msg.channel, irc.network)
        if ignoreUrlRe:
            try:
                ignoreUrlRe = re.compile(ignoreUrlRe)
            except Exception:
                ignoreUrlRe = None

        reportErrors = self.registryValue('reportErrors', msg.channel, irc.network)
        smurfMultipleURLs = self.registryValue('smurfMultipleUrls', msg.channel, irc.network)

        for url in utils.web.httpUrlRe.findall(text):
            if ignoreUrlRe and ignoreUrlRe.search(url):
                continue

            try:
                result = self.getTitle(irc, msg, url)
                if result:
                    (title, domain) = result

                    irc.reply(_('>> %s (at %s)') % (title, domain), prefixNick=False)
            except SmurfException as e:
                if reportErrors:
                    irc.reply(_('!! Error fetching title for %s: %s') % (e.domain, e.message), prefixNick=False)

            if not smurfMultipleURLs:
                break

    @wrap([
        'url',
    ])
    def smurf(self, irc, msg, args, url):
        '''<url>

        Fetch title from URL
        '''

        reportErrors = self.registryValue('reportErrors', msg.channel, irc.network)

        try:
            result = self.getTitle(irc, msg, url)
            if result:
                (title, domain) = result
                irc.reply(_('>> %s (at %s)') % (title, domain))
            else:
                irc.reply(_('!! No title found'))
        except SmurfException as e:
            if reportErrors:
                irc.reply(_('!! Error fetching title for %s: %s') % (e.domain, e.message))

        pass

    def getEncoding(self, text):
        try:
            match = re.search(utils.web._charset_re, text, re.MULTILINE)
            if match:
                return match.group('charset')[1:-1]
        except:  # noqa
            match = re.search(utils.web._charset_re.encode(), text, re.MULTILINE)
            if match:
                return match.group('charset').decode()[1:-1]

        try:
            import charset_normalizer
            result = charset_normalizer.detect(text)
            return result['encoding']
        except:  # noqa
            return None

    def getTitle(self, irc, msg, url):
        # Some things stolen from:
        #   https://github.com/progval/Limnoria/blob/master/plugins/Web/plugin.py
        #   https://github.com/impredicative/urltitle/blob/master/urltitle/config/overrides.py
        max_size = conf.supybot.protocols.http.peekSize()
        timeout = self.registryValue('timeout')
        headers = conf.defaultHttpHeaders(irc.network, msg.channel)

        parsed_url = utils.web.urlparse(url)
        netloc = parsed_url.netloc

        if parsed_url.netloc in ('youtube.com', 'youtu.be') or parsed_url.netloc.endswith(('.youtube.com')):
            max_size = max(max_size, 524288)
        elif parsed_url.netloc in ('reddit.com', 'www.reddit.com', 'new.reddit.com'):
            parsed_url = parsed_url._replace(netloc='old.reddit.com')
            url = urlunparse(parsed_url)
        elif parsed_url.netloc in ('mobile.twitter.com', 'twitter.com'):
            max_size = max(max_size, 65536)
            parsed_url = parsed_url._replace(netloc='twitter.com')
            url = urlunparse(parsed_url)
            headers['User-agent'] = 'Googlebot-News'
        elif parsed_url.netloc in ('github.com'):
            max_size = max(max_size, 65536)
        elif parsed_url.netloc in ('c0re.pfoo.org'):
            headers['User-agent'] = 'Googlebot-News'

        try:
            if parsed_url.netloc == 'twitter.com':
                response = requests.get(url, timeout=timeout, headers=headers)
                text = response.text
            else:
                t = time()
                size = 0
                text = b''

                response = requests.get(url, stream=True, timeout=timeout, headers=headers)
                for chunk in response.iter_content(max_size):
                    size += len(chunk)
                    text += chunk

                    if size >= max_size:
                        break
                    if time() - t > timeout:
                        self.log.error(_('Smurf: URL <%s> timed out'), url)
                        raise SmurfException(parsed_url.netloc, _('Timeout'))

                try:
                    text = text.decode(self.getEncoding(text) or 'utf8', 'replace')
                except UnicodeDecodeError:
                    self.log.error(_('Smurf: URL <%s> - Cannot guess encoding'), url)
                    raise SmurfException(parsed_url.netloc, _('Cannot guess encoding'))
        except SmurfException:
            raise
        except Exception as e:
            self.log.error(_('Smurf: URL <%s> raised <%s>'), url, str(e))
            raise SmurfException(parsed_url.netloc, str(e))

        try:
            parser = SmurfParser()
            parser.feed(text)
        except Exception as e:
            raise SmurfException(parsed_url.netloc, str(e))
        finally:
            parser.close()

        title = utils.str.normalizeWhitespace(''.join(parser.data).strip())
        if title:
            return (title, netloc)

        # Quietly weep...


class SmurfParser(utils.web.HtmlToText):
    entitydefs = entitydefs.copy()
    entitydefs['nbsp'] = ' '

    def __init__(self):
        self.inTitle = False
        self.inSvg = False
        super().__init__(self)

    @property
    def inHtmlTitle(self):
        return self.inTitle and not self.inSvg

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.inTitle = True
        elif tag == 'svg':
            self.inSvg = True

    def handle_endtag(self, tag):
        if tag == 'title':
            self.inTitle = False
        elif tag == 'svg':
            self.inSvg = False

    def append(self, data):
        if self.inHtmlTitle:
            super().append(data)


class SmurfException(Exception):
    def __init__(self, domain, message):
        super().__init__(message)
        self.domain = domain
        self.message = message


Class = Smurf

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
