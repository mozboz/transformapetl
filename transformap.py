#!/usr/bin/env python
# coding: utf-8

import urllib
import logging
import logging.config
import json
import argparse
import yaml
import sys

from sqlalchemy import exists
from datetime import datetime

from transformap.extract import ExtractHttp
from transformap.transform import TransformGeojson
from transformap.load import Load


# Run ETL process

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest="input_file", default=None, help="Path to a job file to process", metavar="input")

    results = parser.parse_args()
        
    logging.config.fileConfig("logging.conf")
    logger = logging.getLogger('Main')
    
    if not results.input_file:
        logger.error("You must specify a job file!")
        sys.exit(1)
    
    # Load config file
    try:
        with open(results.input_file, 'r') as f:
            config = yaml.load(f)
    except IOError:
        logger.error("Job file does not exist!")
        sys.exit(1)
    
    # Extract
    p = config.get('extract').get('type')
    p = p[0].upper() + p[1:].lower()
    EX = eval('Extract%s' % p)(config)
    extractor_response = EX.run()
    
    # Transform
    f = config.get('transform').get('type')
    f = f[0].upper() + f[1:].lower()
    TR = eval('Transform%s' % f)(config)
    
    if extractor_response:
        transformer_response = TR.run(extractor_response)
    else:
        logger.error("Extraction failed")
        sys.exit(1)
    
    # Load
    LD = Load(config)
    if transformer_response:
        load_response = LD.run(transformer_response)
    else:
        logger.error("Transform failed")
        sys.exit(1)
    
    # Exit
    if load_response:
        logger.info("Done!")
    else:
        logger.error("Load failed")
    
    
    
    


    