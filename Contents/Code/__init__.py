# __author__ = 'traitravinh'
import urllib
import urllib2
import re
from BeautifulSoup import BeautifulSoup
################################## Nhaccuatui #########################################
NAME = "Nhaccuatui"
BASE_URL = "http://www.nhaccuatui.com/"
SEARH_URL = 'http://www.nhaccuatui.com/tim-kiem?q=%s'
LOGO = 'http://stc.id.nixcdn.com/10/images/logo_600x600.png'
DEFAULT_ICO = 'icon-default.png'
SEARCH_ICO = 'icon-search.png'
NEXT_ICO = 'icon-next.png'
ART = 'icon-art.png'
##### REGEX #####

# ###################################################################################################

def Start():
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    ObjectContainer.title1 = NAME
    ObjectContainer.view_group = 'List'
    ObjectContainer.art = R(ART)

    DirectoryObject.thumb = R(DEFAULT_ICO)
    DirectoryObject.art = R(ART)

    InputDirectoryObject.thumb=R(DEFAULT_ICO)

    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:22.0) Gecko/20100101 Firefox/22.0'
    HTTP.Headers['X-Requested-With'] = 'XMLHttpRequest'
####################################################################################################

@handler('/video/nhaccuatui', NAME, art=ART, thumb=DEFAULT_ICO)
def MainMenu():
    oc = ObjectContainer()
    oc.add(InputDirectoryObject(
        key=Callback(Search),
        title='SEARCH'
    ))
    link = HTTP.Request(BASE_URL,cacheTime=3600).content
    soup = BeautifulSoup(link)
    a_rel = soup('a',{'rel':'follow'})
    for a in range(0,3):
        asoup = BeautifulSoup(str(a_rel[a]))
        alink = asoup('a')[0]['href']
        atitle = asoup('a')[0].contents[0]
        oc.add(DirectoryObject(
            key=Callback(Index, title=atitle, ilink=alink, ithumb=R(DEFAULT_ICO)),
            title=atitle.decode('utf-8'),
            thumb=R(DEFAULT_ICO)
        ))
    return oc

@route('/video/nhaccuatui/index')
def Index(title, ilink, ithumb):
    oc = ObjectContainer(title2=title)
    if str(ilink).find('video-moi')!=-1:
        ilink = ilink.replace('video-moi','video')
    link = HTTP.Request(ilink,cacheTime=3600).content
    soup = BeautifulSoup(link)
    dashboard = soup('ul', {'class':['notifi video width930','detail_menu_browsing_dashboard']})
    menulist = BeautifulSoup(str(dashboard))('a')
    for m in range(1,len(menulist)):
        msoup = BeautifulSoup(str(menulist[m]))
        mlink = msoup('a')[0]['href']
        mtitle = msoup('a')[0]['title']
        oc.add(DirectoryObject(
            key=Callback(Menu, title=mtitle, mlink=mlink, mthumb=ithumb),
            title=mtitle.decode('utf-8'),
            thumb=ithumb
        ))
    return oc

@route('/video/nhaccuatui/menu')
def Menu(title, mlink, mthumb):
    oc = ObjectContainer(title2=title)
    link = HTTP.Request(mlink,cacheTime=3600).content
    soup = BeautifulSoup(link)
    items = soup('div',{'class':['info_song','box_left']})
    cname='Audio'
    if len(items)<=1:
        items = soup('div',{'class':'box_absolute'})
        cname='Video'
    for i in range(1,len(items)):
        menu_soup = BeautifulSoup(str(items[i]))
        ilink = menu_soup('a')[0]['href']
        ititle = menu_soup('a')[0]['title']
        if str(items[i]).find('<img')!=-1:
            iimage = menu_soup('img')[0]['src']
        else:
            iimage = LOGO
        oc.add(DirectoryObject(
            key=Callback(Episodes, title=ititle, eplink=ilink, cname=cname, epthumb=iimage),
            title=ititle.decode('utf-8'),
            thumb=iimage
        ))
    try:
        pageview =BeautifulSoup(str(soup('div',{'class':'box_pageview'})[0]))('a')
        for p in pageview:
            try:
                p['class']  #active_page
            except KeyError:
                psoup = BeautifulSoup(str(p))
                ptitle = psoup('a')[0].contents[0]
                plink = psoup('a')[0]['href']
                oc.add(DirectoryObject(
                    key=Callback(Menu, title=ptitle, mlink=plink, mthumb=mthumb),
                    title=ptitle,
                    thumb=R(NEXT_ICO)
                ))
    except:pass

    return oc

@route('/video/nhaccuatui/search')
def Search(query=None):
    if query is not None:
        url = SEARH_URL % (String.Quote(query, usePlus=True))
        return Category(query, url)

####################################################################################################
@route('/video/nhaccuatui/category')
def Category(title, catelink):
    oc = ObjectContainer(title2=title)
    link = HTTP.Request(catelink,cacheTime=3600).content
    newlink = ''.join(link.splitlines()).replace('\t','')
    match = re.compile('<ul class="search_control_select">(.+?)<a href="javascript:').findall(newlink)
    li_soup = BeautifulSoup(str(match[0].replace('\t','')))('a')

    for i in range(1,4):
        a_soup = BeautifulSoup(str(li_soup[i]))
        alink = a_soup('a')[0]['href']
        atitle = a_soup('a')[0]['title'].encode('utf-8')
        acount=a_soup('span')[0].contents[0]
        newtitle = atitle + str(acount)

        oc.add(DirectoryObject(
            key=Callback(Servers, title=newtitle, slink=alink, cname=atitle, sthumb=R(DEFAULT_ICO)),
            title=newtitle.decode('utf-8'),
            thumb=R(DEFAULT_ICO)
        ))
    return oc

####################################################################################################
@route('/video/nhaccuatui/servers')
def Servers(title, slink, cname, sthumb):
    image = LOGO
    key = ''
    subkey =''
    oc = ObjectContainer(title2=title)
    link = HTTP.Request(slink,cacheTime=3600).content
    newlink = ''.join(link.splitlines()).replace('\t','')

    if cname.find('B')!=-1:
        key='list_song'
        subkey = 'name_song'
        match = re.compile('<ul class="search_returns_list">(.+?)<div class="box_pageview">').findall(newlink)
    elif cname.find('P')!=-1:
        key = 'list_album'
        subkey = 'box_absolute'
        match = re.compile('<ul class="search_returns_list">(.+?)<div class="box_pageview">').findall(newlink)
    elif cname.find('V')!=-1:
        key = 'list_video'
        subkey = 'img'
        match = re.compile('<ul class="search_returns_list">(.+?)<div class="box_pageview">').findall(newlink)

    soup = BeautifulSoup(match[0].replace('\t','').decode('utf-8'))
    lists = soup('li',{'class':key})
    for l in lists:
        asoup = BeautifulSoup(str(l))
        alink = asoup('a',{'class':subkey})[0]['href']
        try:
            aimage = asoup('img')[0]['src']
            image = aimage
        except:pass
        atitle = asoup('a',{'class':subkey})[0]['title'].encode('utf-8')

        oc.add(DirectoryObject(
            key=Callback(Episodes, title=atitle, eplink=alink, cname=cname, epthumb=image),
            title=atitle.decode('utf-8'),
            thumb=image
        ))

    match_page = re.compile('<div class="box_pageview">(.+?)</div>').findall(newlink)

    pages = BeautifulSoup(str(match_page[0].replace('\t',''))).findAll('a')
    for p in pages:
        psoup = BeautifulSoup(str(p))
        try:
            pactive=str(psoup('a',{'class':'active'})[0])
        except:
            plink = psoup('a')[0]['href']
            ptitle = psoup('a')[0].contents[0]
            if ptitle=='&larr;':
                ptitle='Previous'
            elif ptitle =='&rarr;':
                ptitle='next'

            oc.add(DirectoryObject(
                key=Callback(Servers, title=ptitle, slink=plink, cname=cname, sthumb=sthumb),
                title=ptitle,
                thumb=sthumb
            ))
    return oc

@route('/video/nhaccuatui/episodes')
def Episodes(title, eplink, cname, epthumb):
    oc = ObjectContainer(title2=title)

    if cname.find('Video')!=-1:
        eplink = eplink.replace('http://www','http://m')
        video = videolinks(eplink)
        url = video
        oc.add(createMediaObject(
            url=url,
            title=title.decode('utf-8'),
            thumb=epthumb,
            art=R(ART),
            rating_key=title.decode('utf-8')
        ))
    else:
        xml_link = getXML(eplink)
        filelinks = getMediaLink(xml_link)
        filetitles = getMediaTitle(xml_link)
        filelinkslenght = len(filelinks)

        for i in range(0, filelinkslenght):
            # if Client.Product and Client.Product in ('Plex Web', 'Web Client', 'Plex for Android', 'Plex Home Theater', 'Plex/iOS'):
            # Log(Client.Platform)
            #     # Log(Client.Product)
            oc.add(createTrackObject(
                url=filelinks[i],
                title=filetitles[i].decode('utf-8'),
                thumb=epthumb,
                art=R(ART),
                rating_key=filetitles[i].decode('utf-8')
            ))

    return oc

@route('/video/nhaccuatui/createTrackObject')
def createTrackObject(url, title, thumb, art, rating_key, include_container=False):
    media_obj = MediaObject(
        audio_codec=AudioCodec.MP3,
        container='mp3'
    )
    track_obj = TrackObject(
        key=Callback(createTrackObject, url=url, title=title, thumb=thumb, art=art, rating_key=rating_key, include_container=True),
        rating_key=rating_key
    )
    track_obj.title = title
    track_obj.thumb = thumb

    media_obj.add(PartObject(key = Callback(PlayAudio, url=url)))
    track_obj.add(media_obj)

    if include_container:
        return ObjectContainer(objects=[track_obj])
    else:
        return track_obj

@route('video/nhaccuatui/playaudio')
def PlayAudio(url):
    return Redirect(url)

@route('/video/nhaccuatui/createMediaObject')
def createMediaObject(url, title, thumb, art, rating_key, include_container=False):

    Log('Play Video - '+title)
    Log(url)
    container = Container.MP4
    video_codec = VideoCodec.H264
    audio_codec = AudioCodec.AAC
    audio_channels = 2
    track_object = EpisodeObject(
        key=Callback(
            createMediaObject,
            url=url,
            title=title,
            thumb=thumb,
            art=art,
            rating_key=rating_key,
            include_container=True
        ),
        title=title,
        thumb=thumb,
        art=art,
        rating_key=rating_key,
        items=[
            MediaObject(
                parts=[
                    PartObject(key=Callback(PlayVideo, url=url))
                ],
                container = container,
                video_resolution = '720',
                video_codec = video_codec,
                audio_codec = audio_codec,
                audio_channels = audio_channels,
                optimized_for_streaming = True
            )
        ]
    )

    if include_container:
        return ObjectContainer(objects=[track_object])
    else:
        return track_object


@indirect
def PlayVideo(url):
    return IndirectResponse(VideoClipObject, key=url)

###################################################################################################
def getXML(url):
    try:
        link = urllib2.urlopen(url).read()
        newlink = ''.join(link.splitlines()).replace('\t','')
        file = re.compile('file=(.+?)" /').findall(str(newlink))[0]
        return file
    except:pass

def getMediaLink(url):
    try:
        link = urllib2.urlopen(url).read()
        newlink = ''.join(link.splitlines()).replace('\t','').replace('\n','')
        match = re.compile('<location>(.+?)</location>').findall(newlink)
        finallink=[]
        for content in match:
            finallink.append(content.replace('<![CDATA[','').replace(']]>','').replace(' ',''))
        return finallink
    except:pass

def getMediaTitle(url):
    try:
        link = urllib2.urlopen(url).read()
        newlink = ''.join(link.splitlines()).replace('\t','').replace('\n','')
        match = re.compile('<title>(.+?)</title>').findall(newlink)
        finaltitle=[]
        for content in match:
            finaltitle.append(content.replace('<![CDATA[','').replace(']]>',''))
        return finaltitle
    except:pass

def index_home(url):
    link = HTTP.Request(url,cacheTime=3600).content
    soup = BeautifulSoup(link)
    a_rel = soup('a',{'rel':'follow'})
    for a in range(0,3):
        asoup = BeautifulSoup(str(a_rel[a]))
        alink = asoup('a')[0]['href']
        atitle = asoup('a')[0].contents[0]
    return alink, atitle

def videolinks(url):
    link = HTTP.Request(url,cacheTime=3600).content
    soup = BeautifulSoup(link)
    video = BeautifulSoup(str(soup('div',{'class':'player-video'})[0]))('a')[0]['href']
    return video


####################################################################################################
