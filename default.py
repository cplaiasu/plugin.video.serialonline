import urllib,urllib2,re,xbmc,xbmcplugin,xbmcaddon,xbmcgui,os,commands,HTMLParser,simplejson
import sys
import htmlcleaner

website = 'http://www.serial-online.ro/';

__version__ = "1.0.2"
__plugin__ = "seriale" + __version__
__url__ = "www.xbmc.com"

settings = xbmcaddon.Addon( id = 'plugin.video.serialonlinero-cplaiasu' )

search_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'search.png' )
movies_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'movies.png' )
movies_hd_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'movies-hd.png' )
tv_series_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'tv.png' )
next_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'next.png' )
seriale_noi_thumb = os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'seriale_noi.png' )

def ROOT():
    addDir('Filme Comedie','http://www.990.ro/filme-comedie-1.html',1,movies_thumb)
    #addDir('Filme actualizate','http://www.990.ro/',2,movies_hd_thumb)
    addDir('Seriale','http://www.serial-online.ro/seriale-online.php',5,tv_series_thumb)
    #addDir('Cauta filme','http://www.990.ro/',3,search_thumb)
    addDir('Ultimele Adaugate','http://www.serial-online.ro',9,seriale_noi_thumb)
    xbmc.executebuiltin("Container.SetViewMode(500)")



def FILME_INFO(url):
    raw=get_url(url)
    cpag = raw.split("<div id='numarpagini'>")[1]
    cpag = cpag.split("</div>")[0]
    match=re.compile('<a.+?href="(.+?)">([0-9]+)</a>.+?', re.IGNORECASE).findall(cpag)
    match.reverse()
    masterlink = re.compile('(.+?)[0-9]+.html', re.IGNORECASE).findall(match[0][0])[0]
    maxpag = match[0][1]
    print masterlink, maxpag   
    x = 1
    while x <= int(maxpag):   
        urlpag='http://www.990.ro/'+masterlink+str(x)+'.html'
        print urlpag
        x=x+1
    content = raw.split("<div align='center' id='coloana-stanga'>")[1]
    content = content.split("<div align='center' id='coloana-dreapta'>")[0]    
    filme=re.compile('width:630px(.+?)<iframe', re.DOTALL).findall(content)
    #print filme[0]
    #<img src='../poze/filme/240/210278.jpg' alt='
    #inf=re.compile("<div.+?><a href='(.+?)'><img src='..(.+?.jpg)'.+?'link'>(.+?)</a> \(([0-9]+)\).+?", re.DOTALL).findall(filme[0])
    #print inf
    for film in filme:
        inf=re.compile("<div.+?><a href='(.+?)'><img src='..(.+?.jpg)'.+'link'>(.+?)</a> \(([0-9]+)\).+<div align='left'.+? font:14px Tahoma;'>(.+?)<.+?<img src='images/nota.png' alt='nota (.+?)'.+Gen:(.+?)</div>.+weight:bold;'>(.+?)</div>", re.DOTALL).findall(film)
        for link, img, titlu, an, titlu_ro, nota, gen, descriere  in inf:
            link = 'http://www.990.ro/'+link
            img = 'http://www.990.ro'+img
            titlu = htmlcleaner.clean(titlu,True)
            titlu_ro = htmlcleaner.clean(titlu_ro).replace("\n","").replace("\t","")
            gen = htmlcleaner.clean(gen).replace("\n","").replace("\t","")
            descriere = htmlcleaner.clean(descriere).replace("\n","").replace("\t","")
            nota = float(nota)/2
            print link, img, titlu, an,titlu_ro , nota, htmlcleaner.clean(gen), htmlcleaner.clean(descriere)
            addDir2(titlu,link,4,img,descriere, img, nota, int(an))
            #print link, img, titlu, an#name,url,mode,iconimage,description,fanart
    
    
        # pagina urmatoare
        
    match=re.compile('.+?-([0-9]+).html', re.IGNORECASE).findall(url)
    nr_pagina = match[0]
    #stop XBMC
    if len(filme)==20:
        addNext('Pagina '+str(int(nr_pagina)+1)+' din '+maxpag,'http://www.990.ro/'+masterlink+str(int(nr_pagina)+1)+'.html', 1, next_thumb)
    #xbmc.executebuiltin("Container.SetViewMode(504)")
 
def EPISOADE_NOI(url):
    link=get_url(url)
    content = link.split('<h2>Ultimele Episoade Adaugate</h2>')[1]
    content = content.split('</ul>')[0]
    #print content
    leg=re.compile('href="(.+?)".+?>(.+?) </a>', re.IGNORECASE).findall(content)
    for legatura,nume in leg:
        nume = nume.strip()
        the_link = 'http://www.serial-online.ro/'+legatura
        addDirSort(nume,the_link,6,'')
        #print nume, the_link

def SERIALE(url):
    link=get_url(url)
    match=re.compile('<li><a.+?href="(.+?.php)" title=".+?">(.+?)</a></li>', re.IGNORECASE).findall(link)
    leg=list(set(match))  
    for legatura,nume in leg:
        nume = nume.strip()
        nume = htmlcleaner.clean(nume, strip=False)
        the_link = 'http://www.serial-online.ro/'+legatura
        addDirSort(nume,the_link,6,'')#fost 7
       
def SEZOANE(url,name):
    link=get_url(url)
    match=re.compile('<h3 align="center" style="color:#000;">(.+?)<', re.IGNORECASE).findall(link)
    #content = link.split(match[0])[1]
    content = link.split('<h3 align="center" style="color:#000;">')#[2]
    for x in range(1, len(content)):
        sezon = match[x-1].replace(' online - s',' - S')
        if " &#187;" in sezon:
            sezon = sezon.replace(' &#187;','')
        sezon = htmlcleaner.clean(sezon)
        continut = content[x]
        addDirSort(sezon,continut,7,'')
        


def EPISOADE(continut,sezon):
    #link=get_url(url)
    #<h3 align="center" style="color:#000;"> Supernatural 2005 online - sezonul 8</h3>
    #match=re.compile('<h3.+?>(.+?)online - (sezonul [0-9]+).*?</h3>', re.IGNORECASE).findall(link)
    match=re.compile('<td class="ep">(.+?)</td><td class="tf">(.+?)</td><td class="ad"><a href="(.+?)".+?target=', re.IGNORECASE).findall(continut)
    #print match
    for episod,nume,legatura  in match:
        legatura=legatura.replace(" ", "%20")        
        #print legatura
        episod = htmlcleaner.clean(episod, strip=False)
        nume = htmlcleaner.clean(nume, strip=False)
        nume = nume.replace('<font color="#000">',"")
        nume = nume.replace('</font>',"")        
        if 'Episodul ' in episod:
            episod = episod.replace('Episodul ',"EP")
        if 'Episod ' in episod:
            episod = episod.replace('Episod ',"EP")
            
        
        sezon=sezon.strip()
        if 'Sezonul ' in sezon:
            sezon = sezon.replace('Sezonul ',"S0")
       
        titlu = sezon+' '+episod+' - '+nume
        addDirSort(titlu,legatura,8,'')
       

def VIDEO_EPISOD(url,name):
   html = get_url(url)  
    #print html
   match=re.compile("<iframe src='(.+?)'", re.IGNORECASE).findall(html)
   if match:    
    vk_link = match[0]
    html_vk = get_url(vk_link)
    content_vk = unicode(html_vk)
    match=re.compile("var vars = ({.+?\"})", re.IGNORECASE).findall(content_vk)
    test=simplejson.loads(match[0])
    try: 
        video=test['url1080']
        link = video.split("?")[0]
        
        addLink(name+'-1080p', link+'?.mp4|referer='+link, '', name)        
    except: pass
    try: 
        video=test['url720'] 
        link = video.split("?")[0]
        addLink(name+'-720p', link+'?.mp4|referer='+link, '', name)     
    except: pass        
    try: 
        video=test['url540'] 
        link = video.split("?")[0]
        addLink(name+'-540p', link+'?.mp4|referer='+link, '', name)     
    except: pass        

    try:
        video=test['url480']
        link = video.split("?")[0]
        addLink(name+'-480p', link+'?.mp4|referer='+link, '', name)     
    except: pass
    try: 
        video=test['url360'] 
        link = video.split("?")[0]
        addLink(name+'-360p', link+'?.mp4|referer='+link, '', name)     
    except: pass        
    
    #link = url.split("?")[0]
    #addLink('Server VK Calitate Maxima', link+'?.mp4|referer='+link, '', name)
    #return link
    

    #addLink('Server VK Calitate Maxima', link+'?.mp4|referer='+link, '', 'Titlu')




def VIDEO(url, name):
    #print 'url video '+url
    #print 'nume video '+name
    # thumbnail
    src = get_url(urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]"))
    match = re.compile("<img src='../(poze/filme/.+?)' alt='.+?'", re.IGNORECASE).findall(src)
    thumbnail = 'http://www.990.ro/'+match[0]
    #print thumbnail
    # calitate film
    match=re.compile('Calitate film: nota <b>(.+?)</b>', re.IGNORECASE).findall(src)
    calitate_film = match[0]
    #print calitate_film
    #link trailer
    try:
        match=re.compile("<iframe width='595' height='335' src='.+?/embed/(.+?)'", re.IGNORECASE).findall(src)
        link_youtube = 'http://www.youtube.com/watch?v='+match[0]
        #print link_youtube
        link_video_trailer = youtube_video_link(link_youtube)
    except:
        link_video_trailer = ''
    # video id
    match=re.compile('990.ro/filme-([0-9]+)-.+?.html', re.IGNORECASE).findall(url)
    video_id = match[0]
    #print video_id

    # fu source
    source_link = 'http://www.990.ro/player-film-'+video_id+'-sfast.html'
    #print source_link
    fu_source = get_fu_link(source_link)
    #print fu_source
    if fu_source['url'] != '':
        addLink('Server FastUpload (calitate video: nota '+calitate_film+')', fu_source['url']+'?.flv|referer='+fu_source['referer'], thumbnail, fu_source['title'])

    # xvidstage source
    #source_link = 'http://www.990.ro/player-film-'+video_id+'-sxvid.html'
    #xv_source = get_xvidstage_link(source_link)
    #if xv_source['url'] != '' :
    #    addLink('Server Xvidstage (calitate video: nota '+calitate_film+')', xv_source['url']+'?.flv', thumbnail, xv_source['title'])
    #
    # link trailer
    #if link_video_trailer != '':
    #    addLink('Trailer film', link_video_trailer+'?.mp4', thumbnail, fu_source['title']+' (trailer)')
    

def get_url(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    try:
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link
    except:
        return False




def get_params():
        param=[]
        paramstring=sys.argv[2]
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

def yt_get_all_url_maps_name(url):
    conn = urllib2.urlopen(url)
    encoding = conn.headers.getparam('charset')
    content = conn.read().decode(encoding)
    s = re.findall(r'"url_encoded_fmt_stream_map": "([^"]+)"', content)
    if s:
        s = s[0].split(',')
        s = [a.replace('\\u0026', '&') for a in s]
        s = [urllib2.parse_keqv_list(a.split('&')) for a in s]

    n = re.findall(r'<title>(.+) - YouTube</title>', content)
    return  (s or [], 
            HTMLParser.HTMLParser().unescape(n[0]))

def yt_get_url(z):
    return urllib.unquote(z['url'] + '&signature=%s' % z['sig'])

def youtube_video_link(url):
    # 18 - mp4
    fmt = '18'
    s, n = yt_get_all_url_maps_name(url)
    for z in s:
        if z['itag'] == fmt:
            if 'mp4' in z['type']:
                ext = '.mp4'
            elif 'flv' in z['type']:
                ext = '.flv'
            found = True
            link = yt_get_url(z)
    return link


def addLink(name,url,iconimage,movie_name):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Movie", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)        
        #xbmcplugin.addSortMethod( handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_LABEL )        
        return ok

def addNext(name,page,mode,iconimage):
    u=sys.argv[0]+"?url="+str(page)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Genre": "Science Fiction" } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        
        return ok
def addDir2(name,url,mode,iconimage,description,fanart,rating,an):
        xbmc.executebuiltin('Container.SetViewMode(50)')
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&description="+str(description)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, 'plot': description, "rating": rating, "year": an} )
        liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        xbmc.executebuiltin('Container.SetViewMode(50)')
        return ok
def addDirSort(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        xbmcplugin.addSortMethod( handle = int(sys.argv[1]), sortMethod = xbmcplugin.SORT_METHOD_LABEL )
       
        return ok
        

params=get_params()
url=None
name=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

if mode==None or url==None or len(url)<1:
        ROOT()
       
elif mode==1:
        print ""+url
        FILME_INFO(url)
        
#elif mode==2:
#        print ""+url
#        FILME_CALITATE_BUNA(url)

#elif mode==3:
#        print ""+url
#        CAUTA(url)

elif mode==4:
        print ""+url+" si nume "+name
        VIDEO(url,name)

elif mode==5:
        print ""+url
        SERIALE(url)

elif mode==6:
        print ""+url+""+name
        #EPISOADE(url)
        SEZOANE(url,name)
        

elif mode==7:
        print ""+url+""+name
        EPISOADE(url,name)

elif mode==8:
        print ""+url+""+name
        VIDEO_EPISOD(url,name)
        
elif mode==9:
        print ""+url
        EPISOADE_NOI(url)
        
elif mode==10:
        print ""+url
        VIDEO_EPISOD_NOU(url)



xbmcplugin.endOfDirectory(int(sys.argv[1]))
                       
