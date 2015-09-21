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
    parser.add_argument('-o', '--out', action='store', dest='out_format', choices=['m3u', 'raw', 'yaml' ], default='m3u', help='Output format')
    parser.add_argument('--udpxy', action='store', dest='udpxy_prefix', help='Use given udpxy url (i.e. http://192.168.0.1/4020)\nThis will convert all igmp/sstp stream prefixes to udp')
    parser.add_argument('-q', '--quality', action='store', dest='quality', choices=['sd','hd','any'], default='any', help='Quality selection')
    parser.add_argument('-s', '--strict', action='store', dest='strict', help='Be strict in quality selection' )
    parser.add_argument('-p', '--provider', action='store', dest='provider', choices=['ghm','wba'], default='ghm', help='Provider (i i think), ghm/wba')

    # process all the arguments
    results = parser.parse_args()

    channels = iprtv.getChannels( 'http://w.stb.zt6.nl/tvmenu/index.xhtml.gz' )

    ## Filter here
    #for c in channels:
    #    for s in c['streams']:
    #        if results.provider not in s['provider']:
    #            continue
            

    # create a channelParser object
    #pprint(iptvchannels)
    if results.out_format == 'raw':
                print( '{} {} {}'. format( c['name'], str(s.get('name')).ljust(20), s['url'].ljust(25) ) )
            #pprint( channels )

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
        

    elif results.out_format == 'udpxy':
        print( 'not done yet' )

# allow this to be a module
if __name__ == '__main__':
    main()

