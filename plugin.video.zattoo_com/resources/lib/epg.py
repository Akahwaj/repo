# -*- coding: utf-8 -*-
import sys
import json
from resources.lib.api import get_json_data
import resources.lib.pyxbmct as pyxbmct

URI = sys.argv[0]
ADDON_HANDLE = int(sys.argv[1])


def list_epg_item(pid, SESSION, pg_hash):
    url = 'https://zattoo.com/zapi/v2/cached/program/power_details/%s?program_ids=%s&complete=True' % (pg_hash, pid)
    json_data = get_json_data(url, SESSION)
    program_info = json.loads(json_data)['programs'][0]
    channel_name = program_info['channel_name'].encode('utf-8')
    cid = program_info['cid']
    countries = program_info['country'].replace('|', ', ').encode('utf-8')
    genres = ', '.join(program_info['g']).encode('utf-8')
    categories = ', '.join(program_info['c']).encode('utf-8')
    directors = ', '.join([d for d in program_info['cr']['director']]).encode('utf-8')
    actors = ', '.join([a for a in program_info['cr']['actor']]).encode('utf-8')
    desc = program_info['d'].encode('utf-8')
    subtitle = (program_info['et'] or '').encode('utf-8')
    thumb = program_info['i']
    title = program_info['t'].encode('utf-8')
    if subtitle:
        title = '%s: %s' % (title, subtitle)
    year = program_info['year']
    text = ''
    if desc:
        text += '[COLOR blue]Plot:[/COLOR] %s\n\n' % desc
    if categories:
        text += '[COLOR blue]Kategorien:[/COLOR] %s' % categories
    if genres:
        text += '\n[COLOR blue]Genre:[/COLOR] %s' % genres
    if countries:
        text += '\n[COLOR blue]Produktionsland:[/COLOR] %s' % countries
    if directors:
        text += '\n[COLOR blue]Direktoren:[/COLOR] %s' % directors
    if actors:
        text += '\n[COLOR blue]Schauspieler:[/COLOR] %s' % actors

    if text:
        title = '[B][COLOR blue]%s[/COLOR][/B] %s' % (channel_name, title)
        if year:
            title = '%s (%i)' % (title, year)
        window = pyxbmct.AddonDialogWindow(title)
        window.connect(pyxbmct.ACTION_NAV_BACK, window.close)
        window.setGeometry(1000, 700, 1, 1)
        box = pyxbmct.TextBox()
        window.placeControl(box, 0, 0)
        box.setText(text)
        window.doModal()
        del window