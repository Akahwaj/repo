# -*- coding: utf-8 -*-

import simple_requests as requests
from common import *
from credentials import Credentials

class Client:

    def __init__(self):
        
        VS_URL = 'http://videoshop.ws.eurosport.com/JsonProductService.svc/'
        CRM_URL = 'https://playercrm.ssl.eurosport.com/JsonPlayerCrmApi.svc/'
        
        self.CRM_LOGIN = CRM_URL + 'Login'
        self.CHANNELS = VS_URL  + 'GetAllChannelsCache'
        self.CATCHUPS = VS_URL  + 'GetAllCatchupCache'
        self.TOKEN = VS_URL  + 'GetToken'
        self.EPG = VS_URL + 'FindUpcomingEPG'

        self.headers = {
            'User-Agent': 'iPhone',
            'Referer': base_url
        }

        self.context = {
            'g': '', 
            'd': '2',
            's': '1',
            'p': '1',
            'b': 'apple'
        }

        self.dvs = {
            'userid': userid, 
            'hkey': hkey, 
            'languageid': '',
        }
        
        self.set_location()
        
    def set_user_data(self):
        if not self.dvs['userid'] and not self.dvs['hkey']:
            self.set_user_ref()

    def set_location(self):
        data = self.get_data(base_url)
        c = re.search("crmlanguageid\s*:\s*'(\d+)'", data)
        if c:
            self.dvs['languageid'] = c.group(1)
        g = re.search("geoloc\s*:\s*'(\w+)'", data)
        if g:
            self.context['g'] = g.group(1)
        log('[%s] geolocation: %s' % (addon_id, self.context['g']))

    def set_user_ref(self):
        credentials = Credentials()
        user_ref = self.ep_login(credentials)
        if user_ref.get('Response', None):
            log('[%s] login: %s' % (addon_id, utfenc(user_ref['Response']['Message'])))
        if user_ref.get('Id', '') and user_ref.get('Hkey', ''):
            self.dvs['userid'] = user_ref['Id']
            addon.setSetting('userid', user_ref['Id'])
            self.dvs['hkey'] = user_ref['Hkey']
            addon.setSetting('hkey', user_ref['Hkey'])
            credentials.save()
        else:
            credentials.reset()
    
    def channels(self):
        encoded = urllib.urlencode({'data':json.dumps(self.dvs), 'context':json.dumps(self.context)})
        url = self.CHANNELS + '?' + encoded
        return self.json_request(url)

    def catchups(self):
        encoded = urllib.urlencode({'data':json.dumps(self.dvs), 'context':json.dumps(self.context)})
        url = self.CATCHUPS + '?' + encoded
        return self.json_request(url)
    
    def epg(self):
        encoded = urllib.urlencode({'data':json.dumps(self.dvs), 'context':json.dumps(self.context)})
        url = self.EPG + '?' + encoded
        return self.json_request(url)
        
    def ep_login(self, credentials):
        login_data = {
            'email': utfenc(credentials.email), 
            'password': utfenc(credentials.password), 
            'udid': addon.getSetting('device_id')
        }
        encoded = urllib.urlencode({'data':json.dumps(login_data), 'context':json.dumps(self.context)})
        url = self.CRM_LOGIN + '?' + encoded
        return self.json_request(url)
        
    def logged_in(self, data):
        if data.get('Response', None):
            code = data['Response']['ResponseCode']
            msg = data['Response']['ResponseMessage']
            if code == 1 or code == 4:
                return True
            else:
                if not code == 2:
                    dialog.ok(addon_name, utfenc(msg))
                log('[%s] error: %s' % (addon_id, utfenc(msg)))
        return False
        
    def token(self):
    
        def get_url():
            encoded = urllib.urlencode({'data':json.dumps(self.dvs), 'context':json.dumps(self.context)})
            return self.TOKEN + '?' + encoded
        
        data = self.json_request(get_url())
        if not self.logged_in(data):
            self.set_user_ref()
            data = self.json_request(get_url())
        return data
        
    def get_data(self, url):
        r = requests.get(url, headers=self.headers, allow_redirects=True)
        if r:
            return r.text
        else:
            log('[%s] error: request failed (%s)' % (addon_id, str(r.status_code)))
            return ''
            
    def json_request(self, url):
        r = requests.get(url, headers=self.headers)
        if r.headers.get('content-type', '').startswith('application/json'):
            return r.json()
        else:
            log('[%s] error: json request failed (%s)' % (addon_id, str(r.status_code)))
            return {}