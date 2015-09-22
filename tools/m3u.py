
def m3uAddItem(m3ulist,channelname,url):
    channelitem = {}
    channelitem['name'] = channelname
    channelitem['url'] = url

    m3ulist.append(channelitem)
    return m3ulist

def parseM3u(m3ulist):
        
    print("#EXTM3U")

    for i in m3ulist:
        print("#EXTINF:-1,", i['name'])
        print(i['url'])


