class m3uParser:

    def __init__(self):
        self.data = []

    def addItem(self,channelName,url):
        item = {}
        item['name'] = channelName
        item['url'] = url

        self.data.append(item)

    def parseM3u(self):
        
        print "#EXTM3U"

        for i in self.data:
            print "#EXTINF:-1,",i['name']
            print(i['url'])

    #def writeM3u(filename):

