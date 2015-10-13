# -*- coding: utf-8 -*-
import urllib,urllib2,re,base64,os,sys
import xbmcplugin,xbmcgui,xbmcaddon,xbmc
from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup, BeautifulSOAP as BS


#------------------eklenecek kısım------------------
import araclar,cozucu
##addon_id = 'script.module.kadz2144'
##__settings__ = xbmcaddon.Addon(id=addon_id)
##__language__ = __settings__.getLocalizedString

#---------------------------------------------------
web="http://www.ddizi1.com"

fileName="ddizi"
#--------------- YENI KOMUTLAR  --------------------
# sayfa taratma --> araclar.get_url(url)
# klasor ekleme --> araclar.addDir(fileName,name, mode, url="", thumbnail="")
# link ekleme   --> araclar.addLink(name,url,thumbnail)
# videolink bulma --> urlList=cozucu.videobul(url)
# sonrasında     --> for url in urlList if not isinstance(urlList, basestring) else [urlList]:
#                               araclar.addlink(name,url,thumbnail) yada playList.add(url)
#---------------------------------------------------
        
def main():
        araclar.addDir(fileName,'Yeniler','yeni(web)',web,"")
        div_list=["Yerli Diziler","Eski Diziler","Tv Showlar","Yabanci Diziler"]
        for x in range(0,4):
                name=div_list[x]
                url=str(x)
                araclar.addDir(fileName,name,"panel(url)",url,"YOK")
                

def yeni(url):
        link=araclar.get_url(url)
        match=re.compile('<div class="dizi-box"><a href="(.*?)"><img src="(.*?)" width="120" height="90" alt="(.*?)"').findall(link)
        for url,thumbnail,name in match:
                araclar.addDir(fileName,name,"resolver(name,url)",url,thumbnail)
def panel(url):
        link=araclar.get_url(web)
        soup=BS(link.decode('utf-8','ignore'))
        div = soup.findAll("div",{"class":"blok-liste"})
        for li in div[int(url)].findAll('li'):#-------------dizi anasayfalari bulur
                url= li.a['href']
                name = li.a.text
                name=name.encode("utf-8")
                araclar.addDir(fileName,name,"kategoriler(url)",url,"YOK") 
def kategoriler(url):                    
        data=araclar.get_url(url)
        match=re.compile('<div class="dizi-box2"><a title="(.*?)" href="(.*?)"><img src="(.*?)"').findall(data)#-----dizi bolumleri bulur
        for name,url,thumbnail in match:
                if not thumbnail:
                     thumbnail="yok"   
                araclar.addDir(fileName,name,"resolver(name,url)",url,thumbnail)
                
        veri=data.strip(' \t\n\r').replace(" ","")
        page=re.compile('class="active"><ahref=".*?">.*?</a></li>\r\n<li><ahref="(.*?)"').findall(veri)# ----- sonraki sayfa
        if page:
                try:
                        url=page[0]
                        araclar.addDir(fileName,'Sonraki Sayfa',kategoriler(url),url,"next")
                except:
                        pass

def resolver(name,url):
        value=[]
        tablist=[]
        urllist=[]
        sayfa=araclar.get_url(url)
        data=sayfa.strip(' \t\n\r').replace(" ","")
        print data
        tek=re.compile('<a href="(.*?)">Tek Part</a>').findall(sayfa)
        parts=re.compile('<ahref="/izle/(.*?)">.*?.Par\xc3\xa7a</a>').findall(data)
        print "************************",parts
        if tek:
                url=tek[0].replace('rel="nofollow',"").replace('"',"").replace('rel=""rel="nofollow',"")
                tablist.append("http://www.ddizi1.com"+url)
        
        if parts:
                for url in parts:
                        url=url.replace('rel="nofollow',"").replace('"',"").replace('rel=""rel="nofollow',"")
                        link="http://www.ddizi1.com/izle/"+url
                        tablist.append(link)
        print "tablist",tablist
        #--------------- IC FONKSIYON SAYFA TARAR --------------------------
        def sub_scan(url):
                
                data=araclar.get_url(url)
                #-----------------------------------------------------------------------
                xml=re.compile('settingsFile: "(.*?)"').findall(data)
                if xml:
                        veri=araclar.get_url(xml[0])
                        veri2=veri.strip(' \t\n\r').replace(" ","")
                        links=re.compile('videoPathvalue="(.*?)"').findall(veri2)
                        i=0
                        for url in links:
                                urllist.append(('xmlPart '+str(i),url))
                                i+=1
                        
                        
                #------------------------------------------------------------------------
                adres=re.compile('encodeURIComponent\(\'(.*?)\'').findall(data)
                if adres:
                        for url in adres if not isinstance(adres, basestring) else [adres]:
                                urllist.append(('yPart ',url))
                        

                        
                #-----------------------------------------------------------------------

                vk=re.compile('iframe src="http://vk.com(.*?)"').findall(data)
                if vk:
                        url="http://vk.com"+vk[0]
                        #--------------------------------eklenecek kısım -------------------------
                        urlList=cozucu.videobul(url)
                        #-----------------liste olarak geri gelir for url in urlList: gerekir-------------#
                        print "cozucu donen veri :"+str(urlList)
                        for url in urlList if not isinstance(urlList, basestring) else [urlList]:
                                urllist.append(("Vk Server",url))
                        
                
                return urllist
        #---------------burdan devam ediyor ----------------
        if len(tablist)>0:
                for url in tablist:
                        sonuc=sub_scan(url)
                
        else:                
                sonuc=sub_scan(url)
                

        if sonuc:
                print "-----------------",sonuc
                play(sonuc)
        else:
                dialog = xbmcgui.Dialog()
                i = dialog.ok(name,"Site uyarısı","     Film Siteye henuz yuklenmedi   ","  Yayınlandıktan sonra yüklenecektir.  ")
                return False 

def play(sonuc):
        xbmcPlayer = xbmc.Player()
        playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        if xbmcPlayer.isPlaying():
                xbmcPlayer.stop()
        playList.clear()
        print "***************",sonuc
        for x in sonuc:
                name=x[0]
                url=x[1]
                if "youtube" in str(url):
                        code=url.replace("http://www.youtube.com/watch?v=","")
                        url='plugin://plugin.video.youtube/?action=play_video&videoid=' + str(code)
                playList.add(url)
                araclar.addLink(name,url,"")
                
        if playList:
               xbmcPlayer.play(playList)
        

##########  eklenecek kısım 2  #####################################

def get_params():
        param=[]
        paramstring=sys.argv[2]
        print paramstring
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

        
              
params=get_params()
url=None
thumbnail=None
name=None
mode=None

try:
        fileName=urllib.unquote_plus(params["fileName"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=urllib.unquote_plus(params["mode"])
except:
        pass
try:
        url=urllib.unquote_plus(params["url"])
except:
        pass

try:
        thumbnail=urllib.unquote_plus(params["thumbnail"])
except:
        pass

print "fileName: "+str(fileName)
print "Name: "+str(name)
print "Mode: "+str(mode)
print "URL: "+str(url)
print "thumbnail: "+str(thumbnail)

if mode == None:
        main()
else:
    exec mode
        


xbmcplugin.endOfDirectory(int(sys.argv[1]))
############################SABIT KISIM BURDA BITIYOR #####################333
