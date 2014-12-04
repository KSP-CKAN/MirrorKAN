#!/usr/bin/env python

import os, sys
from distutils.version import LooseVersion
from dateutil.parser import parse
from datetime import datetime, timedelta
import json
import operator
import pytz
import PyRSS2Gen

from mirrorkan import parse_ckan_metadata_directory
from mirrorkan_conf import *
from mirrorkan_util import find_files_with_extension


class EnhancedRSS2(PyRSS2Gen.RSS2):
    def publish_extensions(self, handler):
        PyRSS2Gen._element(handler, 'atom:link', None, {
            'href': LOCAL_URL_PREFIX + "feed/ckan.rss",
            'rel': 'self',
            'type': 'application/rss+xml'})


def main():
    print 'Building CKAN RSS Feed..'

    ckan_files, ckan_json = parse_ckan_metadata_directory(LOCAL_CKAN_PATH)

    unsorted_feed_path = os.path.join(FEED_PATH, 'unsorted.json')
    with open(unsorted_feed_path, 'w') as unsorted_feed_file:
        print 'Writing %s' % unsorted_feed_path
        json.dump(ckan_json, unsorted_feed_file, indent=4, sort_keys=True)    

    sorted_ckan_json = sorted(ckan_json, key=lambda ckan: ckan[0].get('x_last_updated_ts'))

    sorted_feed_path = os.path.join(FEED_PATH, 'sorted.json')
    with open(sorted_feed_path, 'w') as sorted_feed_file:
        print 'Writing %s' % sorted_feed_path
        json.dump(sorted_ckan_json, sorted_feed_file, indent=4, sort_keys=True)    

    rssitems = []

    module_number = 1000000
    for ckan_module in sorted_ckan_json:
        module_number = module_number + 1
        # Fallback for link in case nothing can be determinded
        link = 'http://kerbalstuff.com/' + str(module_number)
        title = ckan_module[0]['name']

        if 'resources' in ckan_module[0]:
            if 'kerbalstuff' in ckan_module[0]['resources']:
                link = ckan_module[0]['resources']['kerbalstuff']
            # elif 'homepage' in ckan_module[0]['resources']:
            # link = ckan_module[0]['resources']['homepage']
            elif 'repository' in ckan_module[0]['resources']:
                link = ckan_module[0]['resources']['repository']

        # Make links unique
        link = link + '#' + str(module_number)

        description = ckan_module[0]['abstract']
        guid = PyRSS2Gen.Guid(link, False)
        pubDate = datetime.fromtimestamp(ckan_module[0].get('x_last_updated_ts', 1000000000), pytz.utc)

        item = PyRSS2Gen.RSSItem(title, 
                                 link,
                                 description,
                                 None, # author
                                 None, # categories
                                 None, # comments
                                 None, # enclosure
                                 guid,
                                 pubDate,
                                 None) # source
        rssitems.append(item)

    rss = EnhancedRSS2(
        title = INDEX_HTML_HEADER + " feed",
        link = LOCAL_URL_PREFIX + "feed/ckan.rss",
        description = "The latest ckan recipes",
        lastBuildDate = datetime.now(pytz.utc),
        items = rssitems)

    rss.rss_attrs = {"version": "2.0", "xmlns:atom": "http://www.w3.org/2005/Atom"}

    rss_feed_path = os.path.join(FEED_PATH, 'ckan.rss')
    with open(rss_feed_path, 'w') as rss_feed_file:
        print 'Writing %s' % rss_feed_path
        rss.write_xml(rss_feed_file)

    print 'Done!'
    
if __name__ == "__main__":
    main()
