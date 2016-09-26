#!/usr/bin/env python
# coding: utf-8

import urllib
import time

from _jobs import Extract


class ExtractHttp(Extract):

    '''
    Fetch a file via HTTP.
    '''

    def run(self):
    
        return {
            'file_name' : 'datagov_1474278205.geojson',
        }

        file_url = self.config.get('extract').get('url')
        
        format = self.config.get('transform').get('format')
        source = self.config.get('transform').get('source')
        file_name = '%s_%s.%s' % (source, int(time.time()), format)
        
        self.logger.info("Saving file %s" % file_name)
        
        try:
            source_file = urllib.URLopener()
            source_file.retrieve(file_url, 'data/%s' % file_name)
        except IOError:
            self.logger.error("IOError: Unable to retrieve file from %s" % file_url)
            return False
        
        return {
            'file_name' : file_name
        }