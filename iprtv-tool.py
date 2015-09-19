#!/usr/bin/python3

import argparse
from pprint import pprint
from tools import iprtv
from tools import m3u

# do the magic here
def main():
    # create an argparser
    parser = argparse.ArgumentParser()
    # add arguments to the parser
    parser.add_argument('--out', action='store', dest='out_format', choices=['m3u', 'raw', 'yaml', 'udpxy'], default='m3u', help='Output format')
    parser.add_argument('--udpxy', action='store', dest='udpxy_prefix', help='Use given udpxy url (i.e. http://192.168.0.1/4020)')

    # process all the arguments
    results = parser.parse_args()

    channels = iprtv.getChannels( 'http://w.stb.zt6.nl/tvmenu/index.xhtml.gz' )
    # create a channelParser object
    #pprint(iptvchannels)
    if results.out_format == 'raw':
        pprint( channels )

    elif results.out_format == 'yaml':
        import yaml
        print( yaml.dump( channels ) )

    elif results.out_format == 'm3u':
        # create a m3uParser object
        m3ulist = m3u.m3uParser()

        for c in channels:
            streams = c['streams']
            for s in streams:
                m3ulist.addItem(c['name'],s['url'])

        # parse whatever has to be parsed
        m3ulist.parseM3u()

    elif results.out_format == 'udpxy':
        print( 'not done yet' )

# allow this to be a module
if __name__ == '__main__':
    main()

