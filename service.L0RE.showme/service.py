#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, sys, os, urlparse
import xbmc ,xbmcgui, xbmcaddon,xbmcvfs
import urllib2,urllib,json
import re,md5,shutil
import socket, cookielib
from datetime import datetime


__addon__ = xbmcaddon.Addon()


profile    = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")
translation = __addon__.getLocalizedString
  

base_url = sys.argv[0]
addon = xbmcaddon.Addon()

profile    = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")
translation = __addon__.getLocalizedString

cj = cookielib.LWPCookieJar();
  
try:
  if xbmcvfs.exists(temp):
    shutil.rmtree(temp)
  xbmcvfs.mkdirs(temp)
except:
  pass
       
# Einlesen von Parametern, Notwendig für Reset der Twitter API
def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict

def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGDEBUG):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 
    
def geturl(url):
   req = urllib2.Request(url)
   inhalt = urllib2.urlopen(req).read()   
   return inhalt   

def geturl(url,data="x",header=[]):
   global cj
   debug("Geturl url:"+url)
   debug("Geturl data:"+data)
   content=""
   opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
   userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
   header.append(('User-Agent', userAgent))
   header.append(('Accept', "*/*"))
   header.append(('Content-Type', "application/json;charset=UTF-8"))
   header.append(('Accept-Encoding', "plain"))   
   opener.addheaders = header
   try:
      if data!="x" :
         request=urllib2.Request(url)
         cj.add_cookie_header(request)
         content=opener.open(request,data=data).read()
      else:
         content=opener.open(url).read()
   except urllib2.HTTPError as e:
       debug ( e)
   opener.close()
   return content
   

        
if __name__ == '__main__':
    debug("START")
    temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")
    monitor = xbmc.Monitor()         
    while not monitor.abortRequested():    
      username=addon.getSetting("username") 
      password=addon.getSetting("password") 
      community=addon.getSetting("community") 
      communitypassword=addon.getSetting("communitypassword")       
      debug("username :"+username)
      debug("password :"+password)
      debug("community :"+community)
      debug("communitypassword :"+communitypassword)      
      if username=="" or password=="" or community=="" or communitypassword=="":
        sleep=60
        if monitor.waitForAbort(sleep):       
           break            
        continue
      else:
        sleep=86400
    
      try:
        serien=xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"VideoLibrary.GetTVShows", "params": {"properties": [ "genre" ]}, "id":"libMovies" }')       
        struktur = json.loads(serien) 
        debug(struktur)
        serien=str(struktur["result"]["limits"]["total"])
        debug("Serien :"+str(serien))
      except:
        serien="0"
        
      try:
          filme=xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"VideoLibrary.GetMovies", "params": {"properties": [ "file" ] }, "id":"libMovies" }')       
          struktur = json.loads(filme) 
          filme=str(struktur["result"]["limits"]["total"])
          debug("filme :"+str(filme))
      except:
          filme="0"
    
      try:
        episodes=xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"VideoLibrary.GetEpisodes", "params": {"properties": [ "file" ] }, "id":"libMovies" }')       
        struktur = json.loads(episodes) 
        episodes=str(struktur["result"]["limits"]["total"])
        debug("Episodes :"+str(episodes))
      except:
         episodes="0"
    
      try:
        lieder=xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"AudioLibrary.GetSongs", "params": {"properties": [ "file" ] }, "id":"libMovies" }')       
        struktur = json.loads(lieder) 
        lieder=str(struktur["result"]["limits"]["total"])
        debug("Lieder :"+str(lieder))
      except:
         lieder="0"
    
      try:
        Alben=xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"AudioLibrary.GetAlbums", "params": {"properties": [ "artist" ] }, "id":"libMovies" }')       
        struktur = json.loads(Alben) 
        Alben=str(struktur["result"]["limits"]["total"])
        debug("Alben :"+str(Alben))
      except:
        Alben="0"
      data='{"user":"'+username+'","password":"'+password+'","comunity":"'+community+'","communitypass":"'+communitypassword+'","songs":'+lieder+',"series":'+serien+',"episodes":'+episodes+',"movies":'+filme+',"alben":'+Alben+'}'
      debug("DATA :")
      debug(data)
      content=geturl("https://l0re.com/kodinerd/inventory.php",data=data)
      debug("++++++")
      debug(content)
      debug("++++++")
      struktur = json.loads(content) 
      if struktur["code"]=="1":
        dialog = xbmcgui.Dialog()
        nr=dialog.ok("Fehler", struktur["msg"])
        sleep=60
      debug(data)

      if monitor.waitForAbort(sleep):       
        break            
           

