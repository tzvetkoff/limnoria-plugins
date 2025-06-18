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
# pylint:disable=missing-function-docstring
# pylint:disable=import-outside-toplevel
# pylint:disable=broad-exception-caught

from re import match
from supybot import conf, registry

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('EMSC')
except Exception:
    def _(x):
        return x


def configure(advanced):
    from supybot.questions import output
    conf.registerPlugin('EMSC', True)
    if advanced:
        output(_('The EMSC plugin sends near-realtime notifications about earthquakes in a configured area.'))


class AreaType(registry.OnlySomeStrings):
    '''Area type. One of "all", "none", "circle" or "rectangle".'''
    validStrings = ('all', 'none', 'circle', 'rectangle')


class AreaCircle(registry.String):
    '''Circle area type'''

    def __init__(self, *args, **kwargs):
        self.errormsg = 'Invalid value. Must be in format "lat,lng,rad", e.g. "42.45,25.5,255.5"'

        self.s = ''
        super().__init__(*args, **kwargs)

    def set(self, s):
        if not s or s in ('none', 'None'):
            self.setValue('')
        elif match(r'^-?\d+(?:\.\d+)?,-?\d+(?:\.\d+)?,\d+(?:\.\d+)?$', s):
            lat, lon, rad = s.split(',')
            lat = float(lat)
            lon = float(lon)
            rad = float(rad)

            self.setValue(f'{lat},{lon},{rad}')
        else:
            self.error(s)


class AreaRectangle(registry.String):
    '''Rectangle area type'''

    def __init__(self, *args, **kwargs):
        self.errormsg = 'Invalid value. Must be in format "lat1,lon1,lat2,lon2", e.g. "34.0,18.0,47.0,32.0"'

        self.s = ''
        super().__init__(*args, **kwargs)

    def set(self, s):
        if not s or s in ('none', 'None'):
            self.setValue('')
        elif match(r'^\d+(?:\.\d+)?,\d+(?:\.\d+)?,\d+(?:\.\d+)?,\d+(?:\.\d+)?$', s):
            lat1, lon1, lat2, lon2 = s.split(',')
            lat1 = float(lat1)
            lon1 = float(lon1)
            lat2 = float(lat2)
            lon2 = float(lon2)

            self.setValue(f'{lat1},{lon1},{lat2},{lon2}')
        else:
            self.error(s)


EMSC = conf.registerPlugin('EMSC')

conf.registerChannelValue(
    EMSC,
    'enable',
    registry.Boolean(False, _('Turns the plugin on/off')),
)
conf.registerChannelValue(
    EMSC,
    'areaType',
    AreaType(
        'none',
        _('Area type (all, none, circle, rectangle)'),
    ),
)
conf.registerChannelValue(
    EMSC,
    'areaCircle',
    AreaCircle(
        '',
        _('Circle GPS coordinates with format "lat,lon,radius"'),
    ),
)
conf.registerChannelValue(
    EMSC,
    'areaRectangle',
    AreaRectangle(
        '',
        _('Rectangle GPS coordinates with format "lat1,lon1,lat2,lon2"'),
    ),
)
conf.registerChannelValue(
    EMSC,
    'minMag',
    registry.Float(2.0, 'Minimal earthquake magnitude')
)
conf.registerChannelValue(
    EMSC,
    'messageFormat',
    registry.String(
        _('Earthquake with magnitude {mag} at coordinates {lat},{lon} ({time}, {flynn_region})'),
        _('Earthquake alert message format'),
    ),
)

# vim:ft=python:ts=4:sts=4:sw=4:et:tw=119
