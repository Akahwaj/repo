# -*- coding: utf-8 -*-

import requests
from credentials import Credentials
from common import *

class Client:

    def __init__(self):
        
        self.headers = {
            'User-Agent': 'iPhone',
            'Referer': video_base,
            'Host': 'video.sport1.de'
        }
        self.cookie = cookie

    def get_playlist(self,id):
        return self.json_request(video_base + '/api/playlist/%s' % (id))

    def get_video(self,id):
        return self.json_request(video_base + '/api/video/%s' % (id))

    def get_tv_epg(self):
        return self.json_request(video_base + '/api/epg/tv')

    def get_fm_epg(self):
        return self.json_request(video_base + '/api/epg/fm')
        
    def get_tv(self, url=False):
        self.headers['Referer'] = tv_base
        self.headers['Host'] = 'tv.sport1.de'
        
        if url:
            if not '/sport1/' in url:
                if not self.logged_in():
                    self.login()
        else:
            url = tv_base + '/mobile/'
        
        if self.cookie:
            self.headers['cookie'] = self.cookie
        
        return self.get_data(url)

    def get_radio(self):
        url = self.get_date()
        self.headers['Referer'] = api_base
        self.headers['Host'] = 'api.sport1.de'
        return self.json_request(url)

    def login(self):
        credentials = Credentials()
        if credentials.email and credentials.password:
            post_data = {
                'log_email': credentials.email,
                'log_pw': credentials.password,
                'log_goback':  '0',
                'log_persistence_cookie': '1'
            }
            url = tv_base + '/mobile/home/index.php'
            r = requests.post(url, headers=self.headers, data=post_data)
            if '<div class="logged-in">' in r.text:
                self.cookie = r.headers['set-cookie']
                addon.setSetting('cookie', self.cookie)
                log('[%s] login successful' % (addon_id))
                credentials.save()
            else:
                pattern = '<span class="loginError.*?">(.*?)</span>'
                s = re.search(pattern, r.text)
                if s:
                    msg = s.group(1)
                else:
                    msg = 'Login Fehlgeschlagen'
                log('[%s] login error: %s' % (addon_id, utfenc(msg)))
                dialog.ok(addon_name, utfenc(msg))
                credentials.reset()

    def logged_in(self):
        self.headers['cookie'] = cookie
        text = self.get_data(tv_base + '/mobile/home/index.php')
        if '<div class="logged-in">' in text:
            self.cookie = cookie
            log('[%s] logged in' % (addon_id))
            return True
        else:
            return False

    def get_date(self):
        data = self.json_request(www_base + '/api/pages/465')
        return data['elements'][0]['elements'][0]['url']
        
    def get_data(self, url):
        r = requests.get(url.replace('https','http'), headers=self.headers)
        if r:
            return r.text
        else:
            return ''
            
    def json_request(self, url):
        r = requests.get(url.replace('https','http'), headers=self.headers)
        if r.headers.get('content-type', '').startswith('application/json'):
            return r.json()
        else:
            log('[%s] error: json request failed with %s response' % (addon_id, str(r.status_code)))
            return {}