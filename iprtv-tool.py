#!/usr/bin/python3

import argparse

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
    print('Hallo.')



# allow this to be a module
if __name__ == '__main__':
    main()

