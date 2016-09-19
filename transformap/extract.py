#!/usr/bin/env python
# coding: utf-8

import urllib
from jobs import Extract


class ExtractHttp(Extract):

    '''
    Fetch a file via HTTP.
    '''

    def run(self):
    
        file_url = self.config.get('extract').get('url')
        
        geojson_file = urllib.URLopener()
        file_name = '%s' % file_url.strip('/').split('/')[-1]
        
        self.logger.info("Retrieving file %s" % file_name)
        
        try:
            geojson_file.retrieve(file_url, 'data/%s' % file_name)
        except IOError:
            self.logger.error("IOError: Unable to retrieve file from %s" % file_url)
            return False
        
        return {
            'file_name' : file_name
        }