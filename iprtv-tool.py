#!/usr/bin/python3

import argparse
from pprint import pprint
from lib.channelparser import channelParser
from lib.m3uparser import m3uParser

# create an argparser
parser = argparse.ArgumentParser()

# add arguments to the parser
parser.add_argument('--parse', action='store', dest='parse_value', choices=['m3u', 'raw', 'udpxy'], default='m3u',
                    help='Output parser format')

parser.add_argument('--udpxy', action='store', dest='udpxy_value', 
                    help='Use given udpxy url (i.e. http://192.168.0.1/4020)')

# process all the arguments
results = parser.parse_args()


# do the magic here
def main():
    
    # create a channelParser object
    cp = channelParser()

    # get the channellist from the channelParser object
    cl = cp.getChannels()
    #pprint(cl)

    # create a m3uParser object
    m3u = m3uParser()

    for channelItem in cl:
        channel = cl[channelItem]

        channelName = channel['name']

        streamList = channel['streams']
        
        for streamItem in streamList:
            url = streamItem.get('url')            
            m3u.addItem(channelName,url)

    # parse whatever has to be parsed
    m3u.parseM3u()

# allow this to be a module
if __name__ == '__main__':
    main()

