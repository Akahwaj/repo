# -*- coding: utf-8 -*-
import urllib
import xbmcaddon
import sys
from resources.lib.functions import get_parameter_dict

addon = xbmcaddon.Addon(id = 'plugin.video.zattoo_com')
SESSION = addon.getSetting('session')

params = get_parameter_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))

if mode == 'watch':
    from resources.lib.watch import get_stream_url
    import xbmcplugin
    import xbmcgui
    MAX_BITRATE = ('600000', '900000', '1500000', '3000000')[int(addon.getSetting('maxQuality'))]
    cid = urllib.unquote_plus(params.get('id', ''))
    stream_url = get_stream_url(cid, SESSION, MAX_BITRATE)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path=stream_url))
else:
    from resources.lib.channels import list_channels
    USE_FANARTS = addon.getSetting('showFanart') == 'true'
    pg_hash = addon.getSetting('pg_hash')
    list_channels(SESSION, pg_hash, USE_FANARTS)