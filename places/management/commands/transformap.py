from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import yaml
import importlib
import logging
import sys

from places.models import *
from _load import Load


class Command(BaseCommand):
    help = 'Run ETL for specified or all clients'

    def add_arguments(self, parser):
        parser.add_argument('--input', '-i', dest='job_file', default=0, help="Job file")


    def handle(self, *args, **options):
    
        job_file = options.get('job_file')
        
        if not job_file:
            logger.error("You must specify a job file!")
            sys.exit(1)
        
        logger = logging.getLogger('main')
        
        # Load config file
        try:
            with open(job_file, 'r') as f:
                config = yaml.load(f)
        except IOError:
            logger.error("Job file does not exist!")
            sys.exit(1)
        
        # Extract
        p = config.get('extract').get('type').title()
        
        module = importlib.import_module('places.management.commands._extract')
        class_ = getattr(module, 'Extract%s' % p)
        EX = class_(config)
        extractor_response = EX.run()
        
        # Transform
        source = config.get('transform').get('source').title()
        format = config.get('transform').get('format').title()
        
        module = importlib.import_module('places.management.commands._transform')
        class_ = getattr(module, 'Transform%s%s' % (source, format))
        TR = class_(config)
        
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