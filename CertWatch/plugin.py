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
# pylint:disable=too-many-arguments
# pylint:disable=bare-except
# pylint:disable=invalid-name
# pyright:reportArgumentType=none
# pyright:reportAttributeAccessIssue=none
# pyright:reportOperatorIssue=none

import ssl
from datetime import datetime, timezone
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.x509.extensions import ExtensionNotFound
from cryptography.hazmat.backends import default_backend

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from supybot import callbacks, ircmsgs, world
from supybot.commands import wrap
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('CertWatch')
except ImportError:
    def _(x):
        return x


class CertWatch(callbacks.Plugin):
    '''Sends notifications about expiring certificates'''
    threaded = True
    job_scheduler = None

    def __init__(self, irc):
        '''Initialize the plugin internal variables'''
        super().__init__(irc)
        self.scheduler_start()

    def die(self):
        self.scheduler_stop()

    def refresh(self):
        for irc in world.ircs:
            for channel in list(irc.state.channels):
                for host in self.registryValue('hosts', channel, irc.network):
                    if ':' not in host:
                        host = f'{host}:443'

                    cert_info = self.cert_info(host)
                    if not cert_info:
                        continue

                    message_format = None
                    if cert_info['days'] >= 2 and cert_info['days'] <= 15:
                        message_format = self.registryValue('messageFormatExpiringMany', channel, irc.network)
                    elif cert_info['days'] == 1:
                        message_format = self.registryValue('messageFormatExpiringOne', channel, irc.network)
                    elif cert_info['days'] == 0 and cert_info['valid']:
                        message_format = self.registryValue('messageFormatExpiringZero', channel, irc.network)
                    elif cert_info['days'] <= 0:
                        cert_info['days'] = abs(cert_info['days'])
                        message_format = self.registryValue('messageFormatExpired', channel, irc.network)
                    if not message_format:
                        continue

                    message = message_format.format_map(cert_info)
                    irc.queueMsg(ircmsgs.privmsg(channel, message))

    def cert_info(self, hostport):
        host, port = hostport.split(':')

        try:
            pem = ssl.get_server_certificate((host, port), timeout=self.registryValue('timeout'))
        except (OSError, ssl.SSLError) as e:
            self.log.warning('CertWatch :: Could not fetch certificate from %s:%d -- %s', host, port, e)
            return None

        try:
            cert = x509.load_pem_x509_certificate(pem.encode(), default_backend)
        except ValueError as e:
            self.log.warning('CertWatch :: Could not parse certificate from %s:%s -- %s', host, port, e)
            return None

        try:
            cn = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        except IndexError:
            self.log.warning('CertWatch :: Certificate from %s:%s does not contain a common name', host, port)
            return None

        alt = []
        try:
            ext = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
            alt = ext.value.get_values_for_type(x509.DNSName)
        except ExtensionNotFound:
            pass

        time_delta = cert.not_valid_after_utc - datetime.now(timezone.utc)

        return {
            'host':           host,
            'port':           port,
            'cn':             cn,
            'alt':            alt,
            'days':           time_delta.days,
            'valid':          time_delta.total_seconds() > 0,
            'expired':        time_delta.total_seconds() < 0,
            'not_before_dt':  cert.not_valid_before_utc,
            'not_before_str': cert.not_valid_before_utc.strftime('%Y-%m-%d %H:%M:%S %Z'),
            'not_after_dt':   cert.not_valid_after_utc,
            'not_after_str':  cert.not_valid_after_utc.strftime('%Y-%m-%d %H:%M:%S %Z'),
        }

    def scheduler_start(self):
        if self.job_scheduler is None:
            self.job_scheduler = BackgroundScheduler()

            time_schedule = self.registryValue('schedule')
            hour, minute = time_schedule.split(':')
            cron_schedule = f'{minute} {hour} * * *'
            self.job_scheduler.add_job(self.refresh, CronTrigger.from_crontab(cron_schedule), id='certwatch_refresh')

            self.job_scheduler.start()

    def scheduler_stop(self):
        if self.job_scheduler is not None:
            self.job_scheduler.shutdown(wait=False)
            self.job_scheduler = None

    def scheduler_restart(self):
        self.scheduler_stop()
        self.scheduler_start()

    def scheduler_refresh(self):
        self.refresh()

    class certwatch(callbacks.Commands):
        @wrap([
            'admin',
            ('literal', {'start', 'stop', 'restart', 'refresh'}),
        ])
        def scheduler(self, irc, _msg, _args, op):
            '''[start|stop|restart]

            Starts/stops/restarts the scheduler.'''

            plugin = irc.getCallback('CertWatch')

            {
                'start':   plugin.scheduler_start,
                'stop':    plugin.scheduler_stop,
                'restart': plugin.scheduler_restart,
                'refresh': plugin.scheduler_refresh,
            }[op]()



Class = CertWatch

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
