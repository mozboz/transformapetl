#!/usr/bin/env python
# coding: utf-8

import orm
import logging, logging.config

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