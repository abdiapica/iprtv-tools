class m3uParser:

    def __init__(self):
        self.m3uitems = []

    def addItem(self,channelName,url):
        channelItem = {}
        channelItem['name'] = channelName
        channelItem['url'] = url

        self.m3uitems.append(channelItem)

    def parseM3u(self):
        
        print("#EXTM3U")

        for i in self.m3uitems:
            print("#EXTINF:-1,", i['name'])
            print(i['url'])

    #def writeM3u(filename):

