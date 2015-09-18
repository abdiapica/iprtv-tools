#!/usr/bin/python3

## Required packages
# apt-get install python3-bs4 python3-requests 

import sys, os
import io, gzip, re
from urllib import request
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pprint import pprint


class channelParser:

    def __init__(self):

        self.iprtv_indexurl = 'http://w.stb.zt6.nl/tvmenu/index.xhtml.gz'

    def getChannels(self):
        # -------------------------------------------------------------------------
        # Goal here is to download the latest code.js, containing all channel data
        #
        # We could just download code.js.gz directly, but let's do it the 'nice' wau
        # by following the directions from index.xhtml.gz
        #
        # We'll end up with variable 'page', containing the full code.js

        # Fetch index file and extract the codejs filename / url
        url =  request.urlopen( self.iprtv_indexurl )
        with gzip.GzipFile( fileobj=io.BytesIO( url.read() ) ) as p:
            page = p.read().decode( 'utf-8', 'ignore' ) 
        soup = BeautifulSoup( page )
        iprtv_codejsurl = urljoin( self.iprtv_indexurl, soup.script['src'] )

        # Fetch and uncomplress the code.js file
        url =  request.urlopen( iprtv_codejsurl )
        with gzip.GzipFile( fileobj=io.BytesIO( url.read() ) ) as p:
            page = p.read().decode( 'utf-8', 'ignore' ) 

        # Remove all linebreaks, that might screw up our regexes later
        page = page.replace( '\n','' )
        page = page.replace( '\r','' )

        # -------------------------------------------------------------------------
        # Distill each javascript blob from the code.js hell
        # Each "channel" starts with [cde].push("name") and ends with b=a
        re_channels = '([cde]\.push\("[ A-z0-9-]*"\).*?b=a)'
        chanjs = re.findall( re_channels, page );
        print( 'number found:',len(chanjs) )


        # -------------------------------------------------------------------------
        # Now, let's loop through each javascript channel blob create a dict of all usefull data
        #
        # We'll search for the following things (with examples)
        # - Chan ID:        e.push("ned1")
        # - Chan type:      I[a].r="tv"
        # - Collection:     K.tv_eng.c.push({d:a})
        # - Chan metadata:  {k:a,b:{"default":"NPO 1"},q:{"default":"NPO 1"},j:"ned1",n:"ned1",w:"npotv1.png",v:"npotv1.png",u:"npotv1.png",o:b,e:[],f:[],g:[]}
        #   Gives, name, icon, etc
        # - Chan webstream: if(Z.h264&&(d.gemist||!h.vodafone&&1))I[a].da={b:{"default":"Uitzending Gemist"},G:"http://npo.app.zt6.nl/app",J:1,H:"npo.r.zt6.nl"}
        #   Gives webstream type, url, etc

        # Dict we'll us (with examples)
        channels = {}

        streams = 0

        # Processing loop
        for cjs in chanjs:
            entry = {}

            # Find the type, either radio or tv
            entry['type']   = re.search( 'I\[a\]\.r="(.*?)"', cjs ).group(1)
            entry['cat'] = re.search( '[IJKL]\.((?:tv|radio)_[a-z]*?)\.[abc]\.push', cjs ).group(1)

            entry['id']  = re.search( '^e\.push\("(.*?)"\)', cjs ).group(1)

            ## Webstreams (some channels have them), before meta, because of BBC Fist
            # da={b:{"default":"Uitzending Gemist"},G:"http://npo.app.zt6.nl/app",J:1,H:"npo.r.zt6.nl"}
            match = re.search( 'da[:=]\{(b:.*?H:".*?")\}', cjs )
            if match:
                c_webstream = self.parseJsDict( match.group(1) )
                entry['webstream'] = {}
                entry['webstream']['url'] = c_webstream['G']
                entry['webstream']['type'] = c_webstream['b']['default']
                entry['webstream']['type2'] = c_webstream['H']

            # {k:a,b:{"default":"NPO 1"},q:{"default":"NPO 1"},j:"ned1",n:"ned1",w:"npotv1.png",v:"npotv1.png",u:"npotv1.png",o:b,e:[],f:[],g:[]}
            c_meta =  re.search( '\{(k:a,b:\{.*?g:\[\])\}', cjs).group(1)
            # Some channels have their 'webstream' item embedded within their meta line.
            # Need to strip that first, incl trailing ','
            c_meta = re.sub( 'da[:=]\{b:.*?H:".*?"\},', '', c_meta )
            c_meta   = self.parseJsDict( c_meta )
            entry['name'] = c_meta['b']['default']
            entry['icon'] = c_meta.get('u')

            # Last, but most definitely the worst of them all, streams. It's why where doing all of this ;)
            c_streams = re.findall( '(if\(A==.*?"(?:igmp|rtsp)://.*?")', cjs )
            entry['streams'] = []
            for s in c_streams:
                stream = {}
                stream['url'] = re.search( '((?:igmp|rtsp)://.*?)(?:;|")', s ).group(1)
                stream['target'] = re.search( '\((A==.*?)\)', s ).group(1).replace('A==','').replace('"','').split('||')
                match = re.search( '{(".*?")}', s )
                if match:
                    stream['name'] = self.parseJsDict( match.group(1) )['default']
                if s.find('rtpskip=yes'):
                    stream['rtpskip'] = 1
                entry['streams'].append( stream )

            # Add to total streamcount
            streams = streams + len(c_streams)

            # Add this channel entry to the main dict
            if len(c_streams) > 0:
                channels[entry['id']] = entry
                
        #pprint( channels )
        #print( 'Total multicast streams found:', streams )
        return channels

        """
        # some useful regexps
        nameregex = '[^"]*'
        ipregex = '[0-9]?[0-9]?[0-9]\.[0-9]?[0-9]?[0-9]\.[0-9]?[0-9]?[0-9]\.[0-9]?[0-9]?[0-9]'
        getrow = re.compile('([cde]\.push\("[ A-z0-9-]*)("\);)(if\(.*?)\{b=([0-9]*);if(.*?),[bc]:{".*?":"(%s)"},[klm]:{".*?":"(%s)"},[gf]:"(%s)",[ij]:"(%s)",[np]:"(%s)"(.*?)(\[[cde]\.pop\(\))' % (nameregex, nameregex, nameregex, nameregex, nameregex))

                #                     1         2             3    4    
                getsubrow = re.compile(';[IJK]\.tv_(.*?)\.[ab]\.push')
                getsubrow = re.compile(';[IJK]\.radio_(.*?)\.[ab]\.push')
                getrow = re.compile('(if\(.*?){(.*?)"igmp://(%s):([0-9]*)(;rtpskip=yes)?"(.*?)\.push' % (ipregex))
                allsubrows = getrow.finditer(item.group(11))
        getrow = re.compile('([cde]\.push\("[ A-z0-9-]*)"\)(;b=)([0-9]*)(.*?),[bc]:{".*?":"(%s)"}(,[klm]:){".*?":"(%s)"}(,[gf]:)"(%s)"(,[ij]:)"(%s)"(,[np]:)"(%s)"(.*?)(\[[cde]\.pop\(\))' % (nameregex, nameregex, nameregex, nameregex, nameregex), re.DOTALL)
            getsubrow = re.compile(';[IJKL]\.tv_(.*?)\.[ab]\.push')
            getsubrow = re.compile(';[IJKL]\.radio_(.*?)\.[ab]\.push')
            getrow = re.compile('(if\(.*?){(.*?)"igmp://(%s):([0-9]*)(;rtpskip=yes)?"(.*?)\.push' % (ipregex))
        sys.exit(0)
        """

    def parseJsDict(self, line):
        # Meta:         k:a,b:{"default":"NPO 1"},q:{"default":"NPO 1"},j:"ned1",n:"ned1",w:"npotv1.png",v:"npotv1.png",u:"npotv1.png",o:b,e:[],f:[],g:[]
        # Webstream:    b:{"default":"Uitzending Gemist"},G:"http://npo.app.zt6.nl/app",J:1,H:"npo.r.zt6.nl"
        ret = {}
        line = re.sub( '[{}"]', '', line )
        variables = line.split(',')
        for var in variables:
            key,value = var.split(':',1)
            if re.search( '[A-z0-9]:[A-z0-9]', value ):
                k,v = value.split(':')
                value = {}
                value[k] = v
            ret[key] = value
        return ret

