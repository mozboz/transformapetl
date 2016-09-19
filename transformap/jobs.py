#!/usr/bin/env python
# coding: utf-8

import orm
import logging, logging.config
import json


class TMJob(object):

    ''' Base Job class '''

    def __init__(self, module_config):
        
        self.orm = orm
        self.session = orm.db_connect()
        self.config = module_config

    def setup_logging(self, name):
    
        logging.config.fileConfig("logging.conf")
        logger = logging.getLogger(name)
        self.logger = logger
        

class Extract(TMJob):
    
    def __init__(self, config):
        self.setup_logging('Extrac')
        super(Extract, self).__init__(config)


class Transform(TMJob):

    def __init__(self, config):
        self.setup_logging('Transf')
        super(Transform, self).__init__(config)
        
    def schema_dict(self):
        '''
        Return schema as dictionary with source field names as keys.
        '''
        map_schema = {}
        for field in self.config.get('transform').get('schema'):
            original_field = field.get('source_field_name')
            map_schema[original_field] = field
        return map_schema
        
    def open_file(self, file_name):
        '''
        Open file and return its contents.
        '''
        with open('data/%s' % file_name) as f:
            data = json.load(f)
        return data