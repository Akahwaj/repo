# -*- coding: utf-8 -*-

from common import *

class Items:

    def __init__(self):
        self.cache = True
        self.video = False
        self.focus = False
    
    def list_items(self, upd=False):
        if self.video:
            xbmcplugin.setContent(addon_handle, content)
            
        xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=self.cache, updateListing=upd)
        
        if force_view:
            xbmc.executebuiltin('Container.SetViewMode(%s)' % view_id)
            
        if self.focus:
            try:
                wnd = xbmcgui.Window(xbmcgui.getCurrentWindowId())
                wnd.getControl(wnd.getFocusId()).selectItem(14)
            except:
                pass

    def add_item(self, item):    
        data = {
                'mode'   : item['mode'],
                'title'  : item['title'],
                'id'     : item.get('id', ''),
                'params' : item.get('params','')
                }
                    
        art = {
                'thumb'  : item.get('thumb', icon),
                'poster' : item.get('thumb', icon),
                'fanart' : fanart
                }
                
        labels = {
                    'title'     : item['title'],
                    'plot'      : item.get('plot', ''),
                    'premiered' : item.get('date', ''),
                    'episode'   : item.get('episode', 0)
                    }
        
        listitem = xbmcgui.ListItem(item['title'])
        listitem.setArt(art)
        listitem.setInfo(type='Video', infoLabels=labels)
        
        if 'play' in item['mode']:
            self.focus = item.get('params', '') == 'Scheduled'
            self.cache = False
            self.video = True
            folder = False
            listitem.addStreamInfo('video', {'duration':item.get('duration', 0)})
            listitem.setProperty('IsPlayable', 'true')
        else:
            folder = True
            
        cm = []
        if item.get('cm', None):
            cm_items = context_items(item['cm'])
            for i in cm_items:
                d = {
                        'mode'   : 'play_context',
                        'title'  : i['title'],
                        'id'     : i.get('id', ''),
                        'params' : i.get('params','')
                        }
                cm.append( (i['type'], 'XBMC.RunPlugin(%s)' % build_url(d)) )
                if len(cm) == 3:
                    break
        if cm:
            listitem.addContextMenuItems( cm )
            
        xbmcplugin.addDirectoryItem(addon_handle, build_url(data), listitem, folder)
        
    def play_item(self, item, name=False, context=False):
        path = item.ManifestUrl
        listitem = xbmcgui.ListItem()
        listitem.setProperty('inputstreamaddon', 'inputstream.mpd')
        listitem.setProperty('inputstream.mpd.license_type', 'com.widevine.alpha')
        listitem.setProperty('inputstream.mpd.license_key', item.LaUrl+'&_widevineChallenge=B{SSM}|||JBlicense')
        if context:
            listitem.setInfo('video', {'Title': name})
            xbmc.Player().play(path, listitem)
        else:
            listitem.setPath(path)
            xbmcplugin.setResolvedUrl(addon_handle, True, listitem)

items = Items()
        
def rails_items(data):
    from rails import Rails
    for i in data.get('Rails', []):
        items.add_item(Rails(i).item)
    items.list_items()
    
def rail_items(data):
    from tiles import Tiles
    for i in data.get('Tiles', []):
        items.add_item(Tiles(i).item)
    items.list_items()
    
def context_items(data):
    cm_items = []
    from tiles import Tiles
    for i in data:
        if i.get('Videos', []):
            cm_items.append(Tiles(i).item)
    return cm_items
    
def playback(data):
    from playback import Playback
    items.play_item(Playback(data))
    
def play_context(data, title):
    from playback import Playback
    items.play_item(Playback(data), name=title, context=True)