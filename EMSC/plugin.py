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

import json
from math import asin, cos, radians, sin, sqrt
from threading import Thread
from websocket import WebSocketApp

from supybot import callbacks, ircmsgs, world
from supybot.commands import optional, wrap
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('EMSC')
except ImportError:
    def _(x):
        return x


class EMSC(callbacks.Plugin):
    '''Sends near-realtime notifications about earthquakes in a configured area.'''
    threaded = True
    ws = None

    def __init__(self, irc):
        '''Initialize the plugin internal variables'''
        super().__init__(irc)
        self.websocket_start()

    def __del__(self):
        self.log.info('Received `del` :: Terminating EMSC connection')
        self.websocket_stop()

    def die(self):
        self.log.info('Received `.die()` :: Terminating EMSC connection')
        self.websocket_stop()

    def on_websocket_message(self, _ws, message):
        # {
        #     "action": "create",
        #     "data": {
        #         "type": "Feature",
        #         "geometry": {
        #             "type": "Point",
        #             "coordinates": [
        #                 -70.15,
        #                 -31.9,
        #                 -134.1
        #             ]
        #         },
        #         "id": "20250612_0000246",
        #         "properties": {
        #             "source_id": "1820120",
        #             "source_catalog": "EMSC-RTS",
        #             "lastupdate": "2025-06-12T22:37:13.950319Z",
        #             "time": "2025-06-12T22:19:22.0Z",
        #             "flynn_region": "SAN JUAN, ARGENTINA",
        #             "lat": -31.9,
        #             "lon": -70.15,
        #             "depth": 134.1,
        #             "evtype": "ke",
        #             "auth": "CSN",
        #             "mag": 2.8,
        #             "magtype": "ml",
        #             "unid": "20250612_0000246"
        #         }
        #     }
        # }
        msg = json.loads(message)
        self.log.info('Received EMSC event: %s', json.dumps(msg, separators=(',', ':')))

        if msg['action'] != 'create':
            return

        for irc in world.ircs:
            for channel in list(irc.state.channels):
                if self.registryValue('enable', channel, irc.network):
                    props = msg['data']['properties']

                    if props['mag'] < self.registryValue('minMag', channel, irc.network):
                        continue

                    area_type = self.registryValue('areaType', channel, irc.network)

                    if area_type == 'none':
                        continue

                    if area_type == 'circle':
                        if not self.point_in_circle(
                            self.registryValue('areaCircle', channel, irc.network),
                            props['lat'],
                            props['lon']
                        ):
                            continue

                    if area_type == 'rectangle':
                        if not self.point_in_rectangle(
                            self.registryValue('areaRectangle', channel, irc.network),
                            props['lat'],
                            props['lon']
                        ):
                            continue

                    props['lat_float'] = props['lat']
                    props['lon_float'] = props['lon']

                    if props['lat'] < 0.0:
                        props['lat'] = f'{abs(props['lat'])}S'
                    elif props['lat'] > 0.0:
                        props['lat'] = f'{props['lat']}N'
                    if props['lon'] < 0.0:
                        props['lon'] = f'{abs(props['lon'])}W'
                    elif props['lon'] > 0.0:
                        props['lon'] = f'{props['lon']}E'

                    message_format = self.registryValue('messageFormat', channel, irc.network)
                    message = message_format.format_map(props)
                    irc.queueMsg(ircmsgs.privmsg(channel, message))

    def haversine(self, lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = radians(lat1), radians(lon1), radians(lat2), radians(lon2)

        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371
        return c * r

    def point_in_circle(self, coords, lat, lon):
        if not coords:
            return False

        clat, clon, crad = coords.split(',')
        clat, clon, crad = float(clat), float(clon), float(crad)

        return self.haversine(clat, clon, lat, lon) <= crad

    def point_in_rectangle(self, coords, lat, lon):
        if not coords:
            return False

        rlat1, rlon1, rlat2, rlon2 = coords.split(',')
        rlat1, rlon1, rlat2, rlon2 = float(rlat1), float(rlon1), float(rlat2), float(rlon2)

        return rlat1 <= lat <= rlat2 and \
               rlon1 <= lon <= rlon2

    @wrap([
        'admin',
        ('literal', {'start', 'stop', 'restart', 'feed'}),
        optional('text'),
    ])
    def websocket(self, _irc, _msg, _args, op, text):
        '''[start|stop|restart]

        Starts/stops/restarts the websocket.'''

        {
            'start':   self.websocket_start,
            'stop':    self.websocket_stop,
            'restart': self.websocket_restart,
            'feed':    lambda: self.websocket_feed(text),
        }[op]()

    def websocket_start(self):
        if self.ws is None:
            self.ws = WebSocketApp(
                'wss://www.seismicportal.eu/standing_order/websocket',
                on_message=self.on_websocket_message,
            )
            Thread(target=self.ws.run_forever, kwargs={'reconnect': 5}).start()

    def websocket_stop(self):
        if self.ws is not None:
            self.ws.close()
            self.ws = None

    def websocket_restart(self):
        self.websocket_stop()
        self.websocket_start()

    def websocket_feed(self, text):
        self.on_websocket_message(self.ws, text)


Class = EMSC

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
