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
# pylint:disable=too-many-ancestors
# pylint:disable=too-many-branches
# pylint:disable=broad-exception-caught
# pyright:reportPrivateUsage=false

import re
import sys
from time import time
from html.entities import entitydefs
from urllib.parse import urlparse, urlunparse
import requests

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

        ignore_url_re = self.registryValue('ignoreUrlRegexp', msg.channel, irc.network)
        if ignore_url_re:
            try:
                ignore_url_re = re.compile(ignore_url_re)
            except Exception:
                ignore_url_re = None

        report_errors = self.registryValue('reportErrors', msg.channel, irc.network)
        show_redirect_chain = self.registryValue('showRedirectChain', msg.channel, irc.network)
        smurf_multiple_urls = self.registryValue('smurfMultipleUrls', msg.channel, irc.network)

        for url in utils.web.httpUrlRe.findall(text):
            if url.endswith(','):
                url = url[:-1]

            if ignore_url_re and ignore_url_re.search(url):
                continue

            try:
                title, domain = self.getTitle(irc, msg, url, show_redirect_chain)
                if title and domain:
                    irc.reply(_('>> %s (at %s)') % (title, domain), prefixNick=False)
            except SmurfException as e:
                if report_errors:
                    irc.reply(_('!! Error fetching title for %s: %s') % (e.domain, e.message), prefixNick=False)

            if not smurf_multiple_urls:
                break

    @wrap([
        'url',
    ])
    def smurf(self, irc, msg, _args, url):
        '''<url>

        Fetch title from URL
        '''

        show_redirect_chain = self.registryValue('showRedirectChain', msg.channel, irc.network)
        report_errors = self.registryValue('reportErrors', msg.channel, irc.network)

        try:
            result = self.getTitle(irc, msg, url, show_redirect_chain)
            if result:
                (title, domain) = result
                irc.reply(_('>> %s (at %s)') % (title, domain))
            else:
                irc.reply(_('!! No title found'))
        except SmurfException as e:
            if report_errors:
                irc.reply(_('!! Error fetching title for %s: %s') % (e.domain, e.message))

    def getEncoding(self, text):
        try:
            match = re.search(utils.web._charset_re, text, re.MULTILINE)    # pylint:disable=protected-access
            if match:
                return match.group('charset')[1:-1]
        except Exception:
            match = re.search(utils.web._charset_re.encode(), text, re.MULTILINE)   # pylint:disable=protected-access
            if match:
                return match.group('charset').decode()[1:-1]

        try:
            import charset_normalizer   # pylint:disable=import-outside-toplevel
            result = charset_normalizer.detect(text)
            return result['encoding']
        except Exception:
            return None

    def getTitle(self, irc, msg, url, show_redirect_chain): # pylint:disable=too-many-locals,too-many-statements
        # Some things stolen from:
        #   https://github.com/progval/Limnoria/blob/master/plugins/Web/plugin.py
        #   https://github.com/impredicative/urltitle/blob/master/urltitle/config/overrides.py
        max_size = conf.supybot.protocols.http.peekSize()
        timeout = self.registryValue('timeout', msg.channel, irc.network)
        headers = conf.defaultHttpHeaders(irc.network, msg.channel)

        parsed_url = urlparse(url)
        netloc = parsed_url.netloc

        if parsed_url.netloc in ('youtube.com', 'youtu.be') or parsed_url.netloc.endswith(('.youtube.com')):
            max_size = max(max_size, 524288)
        elif parsed_url.netloc in ('reddit.com', 'www.reddit.com', 'new.reddit.com'):
            parsed_url = parsed_url._replace(netloc='old.reddit.com')
            url = urlunparse(parsed_url)
        elif parsed_url.netloc in ('mobile.twitter.com', 'twitter.com'):
            parsed_url = parsed_url._replace(netloc='twitter.com')
            url = urlunparse(parsed_url)
            headers['User-agent'] = 'Googlebot-News'
        elif parsed_url.netloc in ('github.com'):
            max_size = max(max_size, 65536)
        elif parsed_url.netloc in ('c0re.pfoo.org'):
            headers['User-agent'] = 'Googlebot-News'

        try:
            if parsed_url.netloc == 'twitter.com' or parsed_url.netloc == 'x.com':
                with requests.get(url, timeout=timeout, headers=headers) as response:
                    text = response.text
            else:
                t = time()
                size = 0
                text = b''

                with requests.get(url, timeout=timeout, headers=headers, stream=True) as response:
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
                except UnicodeDecodeError as e:
                    self.log.error(_('Smurf: URL <%s> - Cannot guess encoding'), url)
                    raise SmurfException(parsed_url.netloc, _('Cannot guess encoding')) from e
        except SmurfException:
            raise
        except Exception as e:
            self.log.error(_('Smurf: URL <%s> raised <%s>'), url, str(e))
            raise SmurfException(parsed_url.netloc, str(e)) from e

        if show_redirect_chain and sys.version_info >= (3, 4):
            try:
                redirect_chain = [urlparse(site.url).netloc for site in response.history]
                redirect_chain = list(dict.fromkeys(redirect_chain))
                redirect_chain.append(urlparse(response.url).netloc)
                netloc = ' -> '.join(redirect_chain)
            except Exception:
                pass

        parser = SmurfParser(parsed_url.netloc)
        try:
            parser.feed(text)
        except Exception as e:
            raise SmurfException(parsed_url.netloc, str(e)) from e
        finally:
            parser.close()

        title = utils.str.normalizeWhitespace(''.join(parser.title()).strip())
        if title:
            return (title, netloc)

        # Quietly weep...
        return (None, None)


class SmurfParser(utils.web.HtmlToText):
    entitydefs = entitydefs.copy()
    entitydefs['nbsp'] = ' '

    def __init__(self, netloc):
        self.netloc = netloc

        self.inside_title_tag = False
        self.inside_svg_tag = False

        self.og_title = None
        self.og_description = None
        self.og_video = None
        self.og_image = None

        super().__init__(self)

    def inside_html_title(self):
        return self.inside_title_tag and not self.inside_svg_tag

    def handle_starttag(self, tag, attr):
        if tag == 'title':
            self.inside_title_tag = True
        elif tag == 'svg':
            self.inside_svg_tag = True
        elif tag == 'meta' and self.netloc in ('twitter.com'):
            attr = dict(attr)

            if 'property' not in attr or 'content' not in attr:
                return

            if attr['property'] == 'og:title':
                self.og_title = attr['content']
            elif attr['property'] == 'og:description':
                self.og_description = attr['content']
            elif attr['property'] == 'og:video':
                self.og_video = attr['content']
            elif attr['property'] == 'og:image':
                self.og_image = attr['content']

    def handle_endtag(self, tag):
        if tag == 'title':
            self.inside_title_tag = False
        elif tag == 'svg':
            self.inside_svg_tag = False

    def append(self, data):
        if self.inside_html_title():
            super().append(data)

    def title(self):
        if self.netloc in ('twitter.com'):
            if self.og_video:
                return f'{self.og_title}: {self.og_description} - {self.og_video}'
            if self.og_image:
                return f'{self.og_title}: {self.og_description} - {self.og_image}'

            return f'{self.og_title}: {self.og_description}'

        return self.data


class SmurfException(Exception):
    def __init__(self, domain, message):
        super().__init__(message)
        self.domain = domain
        self.message = message


Class = Smurf

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
