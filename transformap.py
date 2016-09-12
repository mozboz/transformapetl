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



class TMJob(object):

    def __init__(self, job_file):
        
        # Set up database connection
        self.session = orm.db_connect()
        
        # Load YAML map config file
        # Job config is stored in self.config
        with open(job_file, 'r') as f:
            self.config = yaml.load(f)


class Extractor(TMJob):

    def run(self):
        
        file_url = self.config.get('file_url')
        return self.fetch_via_http(file_url)

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
        return self.transform_geojson(file_name)
    
    def transform_geojson(self, file_name):
    
        '''
        Transform map data in file according to schema.
        '''
    
        logger.info("Transforming data according to schema")
        
        # Get schema
        schema = self.config.get('schema')
        transformed_data = []
        
        # Open source file
        with open('data/%s' % file_name) as f:
            data = json.load(f)
        
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
                    new_field_name = schema[field].get('name')
                    new_row[new_field_name] = value 
            transformed_data.append(new_row)
        
        return {
            'map_data' : transformed_data,
            'file_name' : file_name,
        }


class Loader(TMJob):
        
    def run(self, transformer_response):
        
        map_data = transformer_response.get('map_data')
        file_name = transformer_response.get('file_name')
        
        new_map = self.initialise_map(file_name)
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
        
    def initialise_map(self, file_name):
    
        ''' 
        Save new map instance metadata to database as needed.
        '''
        
        # Map Owner (if necessary)
        map_owner = self.session.query(orm.MapOwner).filter_by(name=self.config.get('owner')).first()
        
        if not map_owner:
            logger.info("Saving new map owner %s" % self.config.get('owner'))
            map_owner = orm.MapOwner(name=self.config.get('owner'))
            self.session.add(map_owner)
            
        # Map Definition (if necessary)
        map_definition = self.session.query(orm.MapDefinition).filter_by(name=self.config.get('definition')).first()
        
        if not map_definition:
            logger.info("Saving new map definition %s" % self.config.get('definition'))
            map_definition = orm.MapDefinition(
                name=self.config.get('definition'),
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
        for field, field_meta in self.config.get('schema', {}).items():
            new_field = orm.SchemaField(
                is_base_field = False,
                schema = schema,
                field_name = field_meta.get('name'),
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
    
    # Set up logging
    logging.config.fileConfig("logging.conf")
    logger = logging.getLogger("Transformap")
    
    job_config = results.input_file
    
    # Fetch and save file
    EX = Extractor(job_config)
    extractor_response = EX.run()
    
    # Transform data
    TR = Transformer(job_config)
    transformer_response = TR.run(extractor_response)
    
    # Load data into database
    LD = Loader(job_config)
    LD.run(transformer_response)
    
    
    
    
    


    