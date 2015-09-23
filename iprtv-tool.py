#!/usr/bin/python3

import argparse
from pprint import pprint
from tools import iprtv
from tools import m3u

# do the magic here
def main():
    # create an argparser
    parser = argparse.ArgumentParser(
        description = 'Fetch a channel list and output various formats, optionally using filters'
    )
    # add arguments to the parser
    parser.add_argument('--dump', action='store_true', dest='dump', help='Just dump the list')
    parser.add_argument('-o', '--out', action='store', dest='out_format', choices=['m3u', 'raw', 'yaml' ], default='m3u', help='Output format')
    parser.add_argument('-u', '--udpxy', action='store', dest='udpxy_prefix', help='Use given udpxy url (i.e. http://192.168.0.1/4020)\nThis will convert all igmp/sstp stream prefixes to udp')
    #parser.add_argument('-q', '--quality', action='store', dest='quality', choices=['sd','hd','any'], default='any', help='Quality selection')
    parser.add_argument('-q', '--quality', action='store', dest='quality', choices=['sd','hd'], default='sd', help='Quality selection')
    parser.add_argument('-p', '--provider', action='store', dest='provider', choices=['ghm','wba'], default='ghm', help='Provider (i i think), ghm/wba')
    parser.add_argument('-s', '--source', action='store', dest='source', choices=['ztv','wba'], default='ztv', help='Provider (i i think), ghm/wba')

    # process all the arguments
    results = parser.parse_args()

    channels = iprtv.getChannels( 'http://w.stb.zt6.nl/tvmenu/index.xhtml.gz' )

    if results.dump:
        import yaml
        print( yaml.dump( channels ) )
        exit()

    filtered = []
    ## Filter here
    for idc, c in enumerate( channels ):
        # Only TV for now
        #if c['type'] != 'tv':
        #    channels.pop(idc)
        #    continue
        for ids, s in enumerate(c['streams']):
            if results.provider not in s['provider']:
                #print( 'skipping privide, filter {}  - chan:{}  stream:{}, {}'.format( results.provider, c['name'], s.get('provider'), s.get('name2') ) )
                channels[idc]['streams'].pop(ids)
                continue
            if results.source not in str(s.get('name2')):
                #if results.quality != 'any' and results.quality in s['name'].lower():
                #print( 'skipping source, filter {} - chan:{}  stream:{}, {}'.format( results.source, c['name'], s.get('provider'), s.get('name2') ) )
                channels[idc]['streams'].pop(ids)
                continue
            if len(c['streams']) > 1:
                if results.quality not in str(s.get('name2')):
                    #print( 'skipping qualit, filter {}  - chan:{}  stream:{}, {}'.format( results.quality, c['name'], s.get('provider'), s.get('name2') ) )
                    channels[idc]['streams'].pop(ids)
                    continue
        if not len(c['streams']):
            #print( 'skipping nostreamsleft - chan:{}  stream:{}, {}'.format( c['name'], s.get('provider'), s.get('name2') ) )
            channels.pop(idc)
            continue
            #if s['name'] and s['name2']:
            #    print('{} has both: {} {} '.format( c['name'], s['name'], s['name2']) )
            #if '239' in s['url']:
            #    print( '{};{};{};{};{}'.format( c['id'], c['name'], s.get('name'), s.get('name2'), s['url'] ) )
        #print( 'keeping filter {}, {}, {}, - chan:{}  stream:{}'.format( results.provider, results.source, results. quality, c['name'], c['streams'] ) )

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

