#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import urlparse
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc
import xbmcvfs
import urllib, urllib2, socket, cookielib, re, os, shutil,json
from StringIO import StringIO
import xml.etree.ElementTree as ET
import time
from datetime import datetime
try:
    import urllib.parse as compat_urllib_parse
except ImportError:  # Python 2
    import urllib as compat_urllib_parse

# Setting Variablen Des Plugins
global debuging
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString

# Es geht um Videos
xbmcplugin.setContent(addon_handle, 'movies')
baseurl="http://www.7tv.de"
icon = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('path')+'/icon.png').decode('utf-8')


profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")


cookie=temp+"/cookie.jar"
cj = cookielib.LWPCookieJar();

if xbmcvfs.exists(cookie):
    cj.load(cookie,ignore_discard=True, ignore_expires=True)


#Directory für Token Anlegen
if not xbmcvfs.exists(temp):       
       xbmcvfs.mkdirs(temp)
       


if xbmcvfs.exists(temp):
  shutil.rmtree(temp)
xbmcvfs.mkdirs(temp)

def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 
    
def addDir(name, url, mode, iconimage, desc=""):
  u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
  ok = True
  liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
  liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
  iconimage = ""
  liz.setProperty("fanart_image", iconimage)	
  liz.setProperty("fanart_image", "")
  ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
  return ok


 
def geturl(url,data="x",header=""):
        global cj
        print("Get Url: " +url)
        for cook in cj:
          debug(" Cookie :"+ str(cook))
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))        
        userAgent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0"
        if header=="":
          opener.addheaders = [('User-Agent', userAgent)]        
        else:
          opener.addheaders = header        
        try:
          if data!="x" :
             content=opener.open(url,data=data).read()
          else:
             content=opener.open(url).read()
        except urllib2.HTTPError as e:
             #print e.code   
             cc=e.read()  
             debug("Error : " +cc)
       
        opener.close()
        return content

   
def addLink(name, url, mode, iconimage, duration="", desc="", genre=''):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
	ok = True
	liz = xbmcgui.ListItem(name, iconImage="", thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre})
	liz.setProperty('IsPlayable', 'true')
	liz.addStreamInfo('video', { 'duration' : duration })
	liz.setProperty("fanart_image", iconimage)
	#liz.setProperty("fanart_image", "")
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
	return ok
  
def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict
 
       
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))

def senderlist():
    inhalt = geturl(baseurl) 
    image_url=re.compile('<link rel="stylesheet" type="text/css" href="(.+?)">', re.DOTALL).findall(inhalt)
    
    kurz_inhalt = inhalt[inhalt.find('<ul class="site-nav-submenu">')+1:]
    kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('</nav>')]  
    match=re.compile('<a href="([^"]+)" [^>]+>([^<]+)</a>', re.DOTALL).findall(kurz_inhalt)
    for id,name in match:
      newurl=baseurl+id      
      debug("#### : "+newurl)
      addDir(name, newurl, "sender", "")      
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def sender(url):
    addDir("Beliebteste Sendungen", url, "belibtesendungen", "")      
    addDir("Neue Ganze Folgen", url, "ganzefolgensender", "")           
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
    
def belibtesendungen(url):
  inhalt = geturl(url) 
  kurz_inhalt = inhalt[inhalt.find('<h3 class="row-headline">Beliebte Sendungen</h3>')+1:]
  kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('<div class="row ">')]  
  spl=kurz_inhalt.split('<article class')
  for i in range(1,len(spl),1):
    try:
      entry=spl[i]
      debug(" ##### ENTRY ####")
      debug(entry)
      urlt=re.compile('href="(.+?)"', re.DOTALL).findall(entry)[0]
      img=re.compile('data-src="(.+?)"', re.DOTALL).findall(entry)[0]
      title=re.compile('teaser-formatname">(.+?)<', re.DOTALL).findall(entry)[0]
      urlv=baseurl+urlt
      debug("belibtesendungen addurl :"+urlv)
      addDir(title, urlv, "serie", img)      
    except:
      pass
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def ganzefolgensender(url):
  inhalt = geturl(url) 
  kurz_inhalt = inhalt[inhalt.find('<h3 class="row-headline">Aktuelle Ganze Folgen</h3>')+1:]
  kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('<h3 class="row-headline">Ihre Favoriten</h3>')]  
  spl=kurz_inhalt.split('<article class')
  for i in range(1,len(spl),1):
    try:
      entry=spl[i]
      if "class-clip" in entry:
        debug(" ##### ENTRY ####")
        debug(entry)
        urlt=re.compile('href="(.+?)"', re.DOTALL).findall(entry)[0]
        img=re.compile('data-src="(.+?)"', re.DOTALL).findall(entry)[0]
        serie=re.compile('<h4 class="teaser-formatname">(.+?)</h4>', re.DOTALL).findall(entry)[0]
        folge=re.compile('<h5 class="teaser-title">(.+?)</h5>', re.DOTALL).findall(entry)[0]
        title=serie + " - " + folge
        urlv=baseurl+urlt
        debug("belibtesendungen addurl :"+urlv)
        addLink(title, urlv, "getvideoid", img)      
    except:
      pass
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)


  
def serie(url):
    debug("serie :"+url)
    addDir("Alle Clips", url+"/alle-clips", "listvideos", "")      
    addDir("Ganze Folgen", url+"/ganze-folgen", "listvideos", "")    
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def sendungsmenu():
    addDir("Sender", "sixx", "allsender", "")      
    addDir("Generes", "Anime", "allsender", "")   
    addDir("Alle Sendungen", baseurl+"/queue/format", "abisz", "")   
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
    
def abisz(url):
  debug("abisz URL :"+url)
  inhalt = geturl(url) 
  struktur = json.loads(inhalt) 
  debug("struktur --------")
  #debug(struktur)
  for buchstabe in struktur["facet"]:
     addDir(buchstabe, url+"/(letter)/"+buchstabe, "jsonfile", "")      
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

def jsonfile(url):
   debug("jsonfile url :"+url)
   inhalt = geturl(url) 
   struktur = json.loads(inhalt) 
   for element in struktur["entries"]:
     urlv=element["url"]
     image=element["images"][0]["url"]
     title=element["title"]
     addDir(title, baseurl+"/"+urlv, "serie", image)       
   xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
   
def allsender(begriff):
  debug("allsender url :"+begriff)
  url="http://www.7tv.de/sendungen-a-z"    
  inhalt = geturl(url) 
  inhalt = inhalt[:inhalt.find('<div class="tvshow-list" data-type="bentobox">')] 
  debug("####### "+inhalt)
  spl=inhalt.split('<ul class="tvshow-filter">')
  for i in range(1,len(spl),1):   
      entry=spl[i]
      debug("Entry :"+ entry)
      if not begriff in entry:
         debug("Nicht gefunden")
         continue
      filter=re.compile('<a href="#tvshow-all" data-href="(.+?)">(.+?)</a>', re.DOTALL).findall(entry)
      for url,name in filter:
         url=baseurl+url
         addDir(name, url, "abisz", "")      
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
  
def listvideos(url):
  inhalt = geturl(url) 
  kurz_inhalt = inhalt[inhalt.find('<div class="main-zone">')+1:]
  kurz_inhalt = kurz_inhalt[:kurz_inhalt.find('<!--googleoff: index-->')]  
  spl=kurz_inhalt.split('<article class')
  for i in range(1,len(spl),1):
    try:
      entry=spl[i]
      debug(" ##### ENTRY ####")
      debug(entry)
      urlv=re.compile('href="(.+?)"', re.DOTALL).findall(entry)[0]
      img=re.compile('data-src="(.+?)"', re.DOTALL).findall(entry)[0]
      title=re.compile('teaser-title">(.+?)</h5>', re.DOTALL).findall(entry)[0]
      urlv=baseurl+urlv
      try:
        match=re.compile('<p class="teaser-info">([0-9]+):([0-9]+) Min.</p>', re.DOTALL).findall(entry)
        zeit=int(match[0][0])*60+ int(match[0][1])
      except:
        zeit=0
        pass
      addLink(title, urlv, "getvideoid", img,duration=zeit)      
    except:
      pass
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True) 

def getvideoid(client_location):
  debug("getvideoid client_location :"+client_location)
  inhalt = geturl(client_location)
  video_id=re.compile('"clip_id": "(.+?)"', re.DOTALL).findall(inhalt)[0]  
  access_token = 'seventv-web'
  salt = '01!8d8F_)r9]4s[qeuXfP%'
  source_id = None
  videos = playvideo(video_id, access_token, "", client_location, salt, source_id)

  
  

def playvideo(video_id, access_token, client_name, client_location, salt, source_id=None):
        from hashlib import sha1

        adaptivaddon=xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddonDetails", "params": {"addonid": "inputstream.adaptive", "properties": ["enabled"]}}')        
        struktur = json.loads(adaptivaddon) 
        is_type=""
        if not "error" in struktur.keys() :            
            if struktur["result"]["addon"]["enabled"]==True:
                is_type="inputstream.adaptive"
        if is_type=="":
          adaptivaddon=xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1, "method": "Addons.GetAddonDetails", "params": {"addonid": "inputstream.mpd", "properties": ["enabled"]}}')        
          struktur = json.loads(adaptivaddon)           
          if not "error" in struktur.keys() :            
            if struktur["result"]["addon"]["enabled"]==True:
                is_type="inputstream.mpd"                
#        if is_type=="":
#          dialog = xbmcgui.Dialog()
          #nr=dialog.ok("Inputstream", "Inputstream fehlt")
          #return ""
        print "is_type :"+is_type
        if source_id is None:
            json_url = 'http://vas.sim-technik.de/vas/live/v2/videos/%s?' \
                       'access_token=%s&client_location=%s&client_name=%s' \
                       % (video_id, access_token, client_location, client_name)
            json_data = geturl(json_url)
            json_data = json.loads(json_data) 
            print json_data
            print "........................"
            if not is_type=="":
              for stream in json_data['sources']:
                if  stream['mimetype']=='application/dash+xml':           
                  source_id = stream['id']
              print source_id
            else:
              #debug("Protected : "+json_data["is_protected"])
              if json_data["is_protected"]==True:
                dialog = xbmcgui.Dialog()  
                nr=dialog.ok("Inputstream", "DRM geschützte Folgen gehen nur mit Inputstream")
                return
              else:
                for stream in json_data['sources']:
                  if  stream['mimetype']=='video/mp4':           
                    source_id = stream['id']
                print source_id
        client_id_1 = salt[:2] + sha1(
            ''.join([str(video_id), salt, access_token, client_location, salt, client_name]).encode(
                'utf-8')).hexdigest()
           
        json_url = 'http://vas.sim-technik.de/vas/live/v2/videos/%s/sources?' \
                   'access_token=%s&client_location=%s&client_name=%s&client_id=%s' \
                   % (video_id, access_token, client_location, client_name, client_id_1)            
        json_data = geturl(json_url)
        json_data = json.loads(json_data) 
        print json_data
        print "........................"
        server_id = json_data['server_id']
        
        client_name = 'kolibri-1.2.5'    
        client_id = salt[:2] + sha1(''.join([salt, video_id, access_token, server_id,client_location, str(source_id), salt, client_name]).encode('utf-8')).hexdigest()
        url_api_url = 'http://vas.sim-technik.de/vas/live/v2/videos/%s/sources/url?%s' % (video_id, compat_urllib_parse.urlencode({
            'access_token': access_token,
            'client_id': client_id,
            'client_location': client_location,
            'client_name': client_name,
            'server_id': server_id,
            'source_ids': str(source_id),
        }))
        print "url_api_url :"+url_api_url
        json_data = geturl(url_api_url)
        json_data = json.loads(json_data) 
        print json_data
        print "........................"        
        data=json_data["sources"][0]["url"]               
        userAgent = 'user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36&Origin=http://www.7tv.de&Referer=http://www.7tv.de/fresh-off-the-boat/25-staffel-2-episode-5-tote-hose-an-halloween-ganze-folge&content-type='
        addon_handle = int(sys.argv[1])
        listitem = xbmcgui.ListItem(path=data)         
        #listitem.setProperty('inputstream.mpd.license_type', 'com.widevine.alpha')
        #listitem.setProperty('inputstream.mpd.license_type', 'com.widevine.alpha')
        listitem.setProperty(is_type+".license_type", "com.widevine.alpha")
        listitem.setProperty(is_type+".manifest_type", "mpd")
        listitem.setProperty('inputstreamaddon', is_type)
        try:
          lic=json_data["drm"]["licenseAcquisitionUrl"]        
          token=json_data["drm"]["token"]                
          listitem.setProperty(is_type+'.license_key', lic +"?token="+token+"|"+userAgent+"|R{SSM}|")            
        except:
           pass
        #listitem.setProperty('inputstreamaddon', 'inputstream.mpd')        
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem)
  
        #print "Daten lic :"+lic
        #print "Daten token :"+token
        #print "Daten data :"+data        
        return ""

        
  
# Haupt Menu Anzeigen      
if mode is '':
    addDir("Sender", "Sender", 'senderlist', "") 
    addDir("Sendungen A-Z", url+"/ganze-folgen", "sendungsmenu", "")  
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
else:
  # Wenn Settings ausgewählt wurde
  if mode == 'Settings':
          addon.openSettings()
  # Wenn Kategory ausgewählt wurde
  if mode == 'senderlist':
          senderlist()
  if mode == 'sender':
          sender(url)
  if mode == 'belibtesendungen':
          belibtesendungen(url)
  if mode == 'serie':
          serie(url)       
  if mode == 'listvideos':
          listvideos(url)       
  if mode == 'getvideoid':
          getvideoid(url)     
  if mode == 'ganzefolgensender':
          ganzefolgensender(url)                      
  if mode == 'sendungsmenu':
          sendungsmenu()                  
  if mode == 'allsender':
          allsender(url)                          
  if mode == 'abisz':
          abisz(url)                                             
  if mode == 'jsonfile':
          jsonfile(url)                                                               