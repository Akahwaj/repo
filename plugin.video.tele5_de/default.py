#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import sys
import re
import os
import xbmcplugin
import xbmcgui
import xbmcaddon
import HTMLParser
import json
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf-8')

#addon = xbmcaddon.Addon()

#addonID = 'plugin.video.tele5_de'
addon = xbmcaddon.Addon()
addonID = addon.getAddonInfo('id')
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
xbmcplugin.setContent(pluginhandle, 'movies')
translation = addon.getLocalizedString
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
baseUrl = "http://www.tele5.de"
opener = urllib2.build_opener()
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0')]

def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 
def getUrl(url,data="x"):
        debug("Get Url: " +url)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        userAgent = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0"
        opener.addheaders = [('User-Agent', userAgent)]
        try:
          if data!="x" :
             content=opener.open(url,data=data).read()
          else:
             content=opener.open(url).read()
        except urllib2.HTTPError as e:
             #debug( e.code)
             cc=e.read()  
             struktur = json.loads(cc)  
             error=struktur["errors"][0] 
             error=unicode(error).encode("utf-8")
             debug("ERROR : " + error)
             dialog = xbmcgui.Dialog()
             nr=dialog.ok("Error", error)
             return ""
             
        opener.close()
        debug(content)
        return content
def index():
  addDir("Uebersicht", baseUrl+"/videos/uebersichtt", "listcat","")
  addDir("Eigenprodutionen", baseUrl+"/videos/eigenproduktionen", "listcat","")
  addDir("Serien", baseUrl+"/videos/serien", "listcat","")
  addDir("Spielfilme", baseUrl+"/filme-online", "listcat","")
  addDir("Lucha Undergroud", baseUrl+"/videos/lucha-underground", "listcat","")
# listcat(baseUrl+"/re-play/uebersicht","listcat")
  xbmcplugin.endOfDirectory(pluginhandle)


def listcat(url,type="listcat"):
      debug("listcat :"+url)
      starturl=url
      content = getUrl(url)
      spl = content.split('ce_teaserelemen')  
      anz=0
      for i in range(1, len(spl), 1):
        element=spl[i]
        try:
          url=re.compile('href="(.+?)"', re.DOTALL).findall(element)[0]
          if not "http" in url:
              url=baseUrl+"/"+url
          try:
            title=re.compile('<h2>(.+?)</h2>', re.DOTALL).findall(element)[0]
          except:
            title=""          
          try:
            subtitle=re.compile('<span class="shortdesc">(.+?)</span>', re.DOTALL).findall(element)[0]          
          except:
            subtitle=""
          if title=="":
            title=subtitle
          else:            
            if not subtitle=="":
                title=title +" - "+subtitle
          thumb=re.compile('srcset="(.+?)"', re.DOTALL).findall(element)[0]    
          debug("listcat URL :"+url)   
          debug("listcat type :"+type)                        
          if not "filme-online" in starturl:
            addDir(title, url, type, baseUrl+"/"+thumb)
          else:    
            debug("++++ URL :"+url)
            idd=re.compile('\?v=(.+)', re.DOTALL).findall(url)[0]               
            debug("++++ idd :"+idd)
            addLink(title, idd, "playVideo", baseUrl+"/"+thumb)
          anz=anz+1
        except:
           pass
      listVideos(starturl)
      xbmcplugin.endOfDirectory(pluginhandle)


def listVideos(url):
          debug("listVideos URL :"+ url)
          content=getUrl(url)                      
          #http://tele5.flowcenter.de/gg/play/l/17:pid=vplayer_1560&tt=1&se=1&rpl=1&ssd=1&ssp=1&sst=1&lbt=1&
          #<div class="fwlist" lid="14" pid="vplayer_3780" tt="1" ssp="1" sst="1" lbt="1" ></div>		</div>
          y=0
          try:    
              debug("1.")          
              divtag=re.compile('(<div class="fwlist".+?>)', re.DOTALL).findall(content)[0]
              debug("DIVTAG :"+divtag)              
              lid=re.compile('lid="(.+?)"', re.DOTALL).findall(divtag)[0]
              debug("LID :"+lid)
              all=re.compile('([^ =]+?)="(.+?)"', re.DOTALL).findall(divtag)
              url="http://tele5.flowcenter.de/gg/play/l/"+lid+":"
              for type,inhalt in all:
               if not type=="lid":
                  url=url+type+"="+inhalt                                    
              #url="http://tele5.flowcenter.de/gg/play/l/"+lid+":pid="+ pid +"&tt="+ tt +"&se="+ se +"&rpl="+ rpl +"&ssd="+ ssd +"&ssp="+ ssp +"&sst="+ sst +"&lbt="+lbt +"&"
              debug("URL: "+url)
          
          except:
            #try:
              y=1
              debug("2.")          
              htmlPage = BeautifulSoup(content, 'html.parser')              
              debug("2a")              
              searchitems = htmlPage.findAll("div",{"class" :"ce_area"})                       
              if len(searchitems) <= 0:
                debug("2a+")
                searchitems = htmlPage.findAll("div",{"class" :"ce_videoelement first block"})                
                debug("+")
              debug("2b")
              for searchitem in searchitems: 
                debug("2c")
                debug(searchitem)                   
                try:          
                  debug(searchitem)                
                  cid=searchitem.find("div",{"class":"fwplayer"})["cid"]                                  
                  debug(":::XX:::"+cid)
                  title=""
                  try:
                    debug("3a")
                    title=searchitem.h3.string
                    utitle=searchitem.p.string
                  except:
                      debug("3b")
                      debug(title+"###")
                      if title=="":
                          debug("3c")
                          contentn=getUrl("https://tele5.flowcenter.de/gg/play/p/"+cid)
                          title=re.compile('"title":"(.+?)"', re.DOTALL).findall(contentn)[0]
                          debug("Title:"+title)
                          utitle=""
                      else:
                          debug("3d")
                          utitle=""
                  if not utitle=="":
                   title=title +" - "+ utitle
                  debug(title)
                  img=searchitem.find('img')['src']
                  if not "http" in img:
                    img="http://www.tele5.de/"+img
                  debug(img)
                  addLink(title, str(cid), 'playVideo', img)    
                except:                   
                   pass
              #playVideo(cid)
            #except:
            #   pass
          if y==0:    
            debug("3.")                    
            debug("NEWURL: "+url)
            content=getUrl(url)
            debug("##########")            

            content=re.compile('\{"id"(.+)\},', re.DOTALL).findall(content)[0]
            content='{"id"'+content+"}"
            debug("CONTENT:")
            debug(content)
            struktur = json.loads(content) 
            Entries=struktur["entries"]
            for element in Entries:
              staffel=element["staffel"]
              folge=element["folge"]
              utitle= element["utitel"].strip()
              title= element["title"].strip()
              id=element["id"]
              data=element["vodate"]
              genre=element["welt"]
              image=element["image"].replace("\/","/")
              if folge=="0":
                name=title
              else:
                 name="Folge "+ folge 
              if not utitle=="" :
                 name=name+" - "+utitle
              addLink(name, str(id), 'playVideo', image,dadd=data,genre=genre,episode=folge,season=staffel)          
              #addLink("Folge :"+ folge , str(id), 'playVideo', image)          
          
              #   addLink(h.unescape(title[i]), url, 'playVideo', thumb[i])          
          xbmcplugin.endOfDirectory(pluginhandle)


def playVideo(url):           
    debug("PlayVideo Url :"+url)
    addon_handle = int(sys.argv[1])
    urlneu="http://tele5.flowcenter.de/gg/play/p/"+url+":mobile=0&nsrc="+url+"&" 
    content = getUrl(urlneu)
    file=re.compile('"file":"(.+?)"', re.DOTALL).findall(content)[-2]
    file=file.replace("\/","/")
    content = getUrl(file)
    mpg=re.compile(' <BaseURL>(.+?)</BaseURL>', re.DOTALL).findall(content)[-1]    
    videofile=file.replace("manifest.mpd",mpg)
    debug("MPG: "+videofile)
    listitem = xbmcgui.ListItem(path=videofile)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def queueVideo(url, name, thumb):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name, thumbnailImage=thumb)
    playlist.add(url, listitem)


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#039;", "\\").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö")
    title = title.strip()
    return title


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def addLink(name, url, mode, iconimage, desc="", duration="",count=0,dadd=0,genre="",episode=0,season=0):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&count="+str(count)
    ok = True
    liz = xbmcgui.ListItem(name)
    liz.setArt({ 'fanart': iconimage })
    liz.setArt({ 'thumb': iconimage })
    liz.setInfo(type="Video", infoLabels={"title": name, "plot": desc, "duration": duration ,"lastplayed": dadd,"genre":genre,"episode":episode,"season":season })
    liz.setProperty('IsPlayable', 'true')
    liz.addContextMenuItems([(translation(30004), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+str(name)+'&thumb='+urllib.quote_plus(iconimage)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage, desc="", duration=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name)
    liz.setArt({ 'fanart': iconimage })
    liz.setArt({ 'thumb': iconimage })
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Duration": duration})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
thumb = urllib.unquote_plus(params.get('thumb', ''))
count  = urllib.unquote_plus(params.get('count', ''))

if mode == 'listVideos':
    listVideos(url)
elif mode == 'listcat':
    listcat(url)
elif mode == 'playVideo':
    playVideo(url)
else:
    index()
