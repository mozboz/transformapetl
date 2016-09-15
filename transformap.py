#!/usr/bin/env python
# coding: utf-8

import urllib
import logging
import logging.config
import json
import argparse
import yaml

from sqlalchemy import exists
from datetime import datetime

import orm
import sys



class TMJob(object):

    def __init__(self, module_config):
        
        # Set up database connection
        self.session = orm.db_connect()
        self.config = module_config


class Extractor(TMJob):

    def run(self):
        
        extract_config = self.config.get('extract')
        
        if extract_config.get('protocol') == 'http':
            return self.fetch_via_http(extract_config.get('url'))
        else:
            logger.error("Unrecognised protocol %s" % extract_config.get('protocol'))   
            return False 

    def fetch_via_http(self, file_url):
    
        '''
        Fetch a file via HTTP and save it to data dir.
        '''
        
        geojson_file = urllib.URLopener()
        file_name = '%s' % file_url.strip('/').split('/')[-1]
        
        logger.info("Retrieving file %s" % file_name)
        geojson_file.retrieve(file_url, 'data/%s' % file_name)
        
        return {
            'file_name' : file_name
        }


class Transformer(TMJob):
        
    def run(self, extractor_response):
    
        file_name = extractor_response.get('file_name')
        file_format = self.config.get('transform').get('format')
        schema = self.config.get('transform').get('schema')
        
        # re-organise schema into dictionary
        map_schema = {}
        for field in schema:
            original_field = field.get('source_field_name')
            map_schema[original_field] = field
            
        # open file
        data = self.open_file(file_name)
            
        # do data transformation
        if file_format == 'geojson':
            transformed_data = self.transform_geojson(data, map_schema)
        else:
            logger.error("Unknown file format %s " % file_format)
            return False
        
        # response
        return {
            'map_data' : transformed_data,
            'file_name' : file_name,
            'map_schema' : map_schema,
        }
            
    def open_file(self, file_name):
        
        # Open source file
        with open('data/%s' % file_name) as f:
            data = json.load(f)
        return data
            
    def transform_geojson(self, data, schema):
    
        '''
        Transform map data in file according to schema.
        '''
    
        logger.info("Transforming data according to schema")
        
        transformed_data = []
        
        # Transform each row
        for row in data.get('features'):
            new_row = {
                'longitude' : row.get('geometry', {}).get('coordinates', {})[0],
                'latitude' : row.get('geometry', {}).get('coordinates', {})[1],
            }
            
            for field, value in row.get('properties').items():
                if field not in schema.keys():
                    continue
                else:
                    new_field_name = schema[field].get('target_field_name')
                    new_row[new_field_name] = value
            transformed_data.append(new_row)
        
        return transformed_data


class Loader(TMJob):
        
    def run(self, transformer_response):
        
        map_data = transformer_response.get('map_data')
        file_name = transformer_response.get('file_name')
        map_schema = transformer_response.get('map_schema')
        
        map_config = {
            'owner': self.config.get('load').get('owner'),
            'definition': self.config.get('load').get('definition'),
            'schema': map_schema
        }
        
        new_map = self.initialise_map(file_name, map_config)
        self.save_map(new_map, map_data)

    def save_map(self, new_map, map_data):
    
        '''
        Save data to database.
        '''
        
        # Fetch schema for this map instance from DB
        map_schema = {}
        schema = self.session.query(orm.SchemaField).filter_by(schema_id=new_map['map_schema'].id).all()
        for schema_field in schema:
            field_name = schema_field.field_name
            field_id = schema_field.id
            map_schema[field_name] = field_id
            
        # Save data to db
        logger.info("Saving map data to database")
        for row in map_data:
            
            # save map object
            map_object = orm.MapObject(
                longitude = row.get('longitude'),
                latitude = row.get('latitude'),
                map_instance = new_map['map_instance'],
            )
            self.session.add(map_object)
            self.session.commit()
            
            # save new rows for object
            for field, value in row.items():
                if field not in ('latitude', 'longitude'):            
                    new_row = orm.MapData(
                        map_instance = new_map['map_instance'],
                        map_object = map_object,
                        schema_field_id = map_schema[field],
                        field_value = value,
                    )
                    self.session.add(new_row)
                    self.session.commit()
                    
        logger.info("Done!")
        
    def initialise_map(self, file_name, map_config):
    
        ''' 
        Save new map instance metadata to database as needed.
        '''
        
        
        # Map Owner (if necessary)
        map_owner = self.session.query(orm.MapOwner).filter_by(name=map_config.get('owner')).first()
        
        if not map_owner:
            logger.info("Saving new map owner %s" % map_config.get('owner'))
            map_owner = orm.MapOwner(name=map_config.get('owner'))
            self.session.add(map_owner)
            
        # Map Definition (if necessary)
        map_definition = self.session.query(orm.MapDefinition).filter_by(name=map_config.get('definition')).first()
        
        if not map_definition:
            logger.info("Saving new map definition %s" % map_config.get('definition'))
            map_definition = orm.MapDefinition(
                name=map_config.get('definition'),
                owner=map_owner,
            )
            self.session.add(map_definition)
            
        # Schema Version
        logger.info("Saving schema version")
        schema = orm.SchemaVersion(
            map_definition = map_definition,
            map_owner = map_owner
        )
        self.session.add(map_definition)
        
        # Map Instance
        logger.info("Saving map instance")
        map_instance = orm.MapInstance(
            schema = schema,
            map_definition = map_definition,
            retrieval_date = datetime.now(),
            source_path = 'data/%s' % file_name,
        )
        
        # Schema Fields
        logger.info("Saving schema fields")
        for field, field_meta in map_config.get('schema').items():

            new_field = orm.SchemaField(
                is_base_field = False,
                schema = schema,
                field_name = field_meta.get('target_field_name'),
                field_type = field_meta.get('type'),
                field_description = field_meta.get('description'),
            )
            self.session.add(new_field)
        
        # Commit to database
        self.session.commit()
        
        return {
            'map_instance' : map_instance,
            'map_schema' : schema,
        }
            

# Run ETL process

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest="input_file", default=None, help="Path to a job file to process", metavar="input")

    results = parser.parse_args()
    
    # Load YAML map config file
    # Job config is stored in self.config
    with open(results.input_file, 'r') as f:
        config = yaml.load(f)
    
    # Set up logging
    logging.config.fileConfig("logging.conf")
    logger = logging.getLogger("Transformap")
    
    # Fetch and save file
    EX = Extractor(config)
    extractor_response = EX.run()
    
    # Transform data
    TR = Transformer(config)
    if extractor_response:
        transformer_response = TR.run(extractor_response)
    else:
        sys.exit(1)
    
    # Load data into database
    LD = Loader(config)
    if transformer_response:
        LD.run(transformer_response)
    else:
        sys.exit(1)
    
    
    
    
    


    