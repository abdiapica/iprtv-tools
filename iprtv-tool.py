#!/usr/bin/python3

import argparse
from pprint import pprint
from tools import iprtv
from tools import m3u

# do the magic here
def main():

    qualities = [ 'sd', 'md', 'hd' ]


    # create an argparser
    parser = argparse.ArgumentParser(
        description = 'Fetch a channel list and output various formats, optionally using filters'
    )
    # add arguments to the parser
    parser.add_argument('--dump', action='store_true', dest='dump', help='Just dump the list')
    parser.add_argument('-o', '--out', action='store', dest='out_format', choices=['m3u', 'raw', 'yaml' ], default='m3u', help='Output format')
    parser.add_argument('-u', '--udpxy', action='store', dest='udpxy_prefix', help='Use given udpxy url (i.e. http://192.168.0.1/4020)\nThis will convert all igmp/sstp stream prefixes to udp')
    #parser.add_argument('-q', '--quality', action='store', dest='quality', choices=['sd','hd','any'], default='any', help='Quality selection')
    parser.add_argument('-p', '--provider', action='store', dest='provider', choices=['ghm','wba'], default='ghm', help='Provider (i i think), ghm/wba')
    parser.add_argument('-s', '--source', action='store', dest='source', choices=['ztv','wba'], default='ztv', help='Source/encryption of the stream?')
    parser.add_argument('-q', '--quality', action='store', dest='quality', choices=qualities, default='sd', help='Quality selection')

    # process all the arguments
    results = parser.parse_args()

    channels = iprtv.getChannels( 'http://w.stb.zt6.nl/tvmenu/index.xhtml.gz' )
    notqualities = qualities
    notqualities.remove(results.quality)

    if results.dump:
        import yaml
        print( yaml.dump( channels ) )
        exit()

    filtered = []
    for c in channels:
        c['streams'] = [ s for s in c['streams'] if results.provider in s.get('provider') ]
        c['streams'] = [ s for s in c['streams'] if results.source in str(s.get('name')).lower() ]
        # If there are multiple streams left, these are different quality streams (SD/HD)
        if len(c['streams']) > 1:
            # First search for stream with the quality in it's name
            qs = [ s for s in c['streams'] if results.quality in str(s.get('name2')).lower() ]
            if len(qs):
                c['streams'] = qs
            else:
                # Search for other qualities and pop them
                for ids, s in enumerate(c['streams']):
                    for nq in notqualities:
                        if s.get('name2'):
                            if nq in str(s.get('name2')).lower():
                                c['streams'].pop(ids)
                        else:
                            if nq in str(s.get('name')).lower():
                                c['streams'].pop(ids)
        if len(c['streams']):
            c['streams'] = c['streams'].pop()
            filtered.append(c)

    channels = filtered

    # create a channelParser object
    #pprint(iptvchannels)
    if results.out_format == 'raw':
        pprint( channels )

    elif results.out_format == 'yaml':
        import yaml
        print( yaml.dump( channels ) )

    elif results.out_format == 'm3u':
        # create a m3u list
        playlist = []

        for c in channels:
            for s in c['streams']:
                if results.udpxy_prefix:
                    playlist = m3u.m3uAddItem( playlist, c['name'], results.udpxy_prefix + s['url'].split('//')[1] )
                else:
                    playlist = m3u.m3uAddItem( playlist, c['name'],s['url'])

        # parse whatever has to be parsed
        m3u.parseM3u( playlist )
        

# allow this to be a module
if __name__ == '__main__':
    main()

