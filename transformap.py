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

class TransforMap():

    def __init__(self, job_file):
    
        # Set up logging
        logging.config.fileConfig("logging.conf")
        self.logger = logging.getLogger("Transformap")
        
        # Set up database connection
        self.session = orm.db_connect()
        
        # Load YAML map config file
        with open(job_file, 'r') as f:
            self.map_config = yaml.load(f)
        
    def fetch_http(self):
    
        '''
        Fetch a file via HTTP and save it to data dir.
        '''
        
        file_url = self.map_config.get('file_url')
        geojson_file = urllib.URLopener()
        file_name = '%s' % file_url.strip('/').split('/')[-1]
        self.logger.info("Retrieving file %s" % file_name)
        geojson_file.retrieve(file_url, 'data/%s' % file_name)
        self.file_name = file_name
        
    def transform_data(self):
    
        '''
        Apply transformation to fields based on schema, 
        return transformed data array.
        '''
        
        self.logger.info("Transforming data according to schema")
        
        # Get schema
        schema = self.map_config.get('schema')
        self.transformed_data = []
        
        # Open source file
        with open('data/%s' % self.file_name) as f:
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
            self.transformed_data.append(new_row)

    def save_map(self):
    
        '''
        Initialise the map instance and save data to the database.
        '''
        
        self.initialise_map()
            
        # Fetch schema for this map instance from DB
        map_schema = {}
        schema = self.session.query(orm.SchemaField).filter_by(schema_id=self.schema.id).all()
        for schema_field in schema:
            field_name = schema_field.field_name
            field_id = schema_field.id
            map_schema[field_name] = field_id
            
        # Save data to db
        self.logger.info("Saving map data to database")
        for row in self.transformed_data:
            
            # save map object
            map_object = orm.MapObject(
                longitude = row.get('longitude'),
                latitude = row.get('latitude'),
                map_instance = self.map_instance,
            )
            self.session.add(map_object)
            self.session.commit()
            
            # save new rows for object
            for field, value in row.items():
                if field not in ('latitude', 'longitude'):            
                    new_row = orm.MapData(
                        map_instance = self.map_instance,
                        map_object = map_object,
                        schema_field_id = map_schema[field],
                        field_value = value,
                    )
                    self.session.add(new_row)
                    self.session.commit()
                    
    """ 
    HELPERS 
    """
        
    def initialise_map(self):
    
        ''' 
        Save new map instance metadata to database as needed.
        '''
        
        map_config = self.map_config
        
        # Map Owner (if necessary)
        map_owner = self.session.query(orm.MapOwner).filter_by(name=map_config.get('owner')).first()
        
        if not map_owner:
            self.logger.info("Saving new map owner %s" % map_config.get('owner'))
            map_owner = orm.MapOwner(name=map_config.get('owner'))
            self.session.add(map_owner)
            
        # Map Definition (if necessary)
        map_definition = self.session.query(orm.MapDefinition).filter_by(name=map_config.get('definition')).first()
        
        if not map_definition:
            self.logger.info("Saving new map definition %s" % map_config.get('definition'))
            map_definition = orm.MapDefinition(
                name=map_config.get('definition'),
                owner=map_owner,
            )
            self.session.add(map_definition)
            
        # Schema Version
        self.logger.info("Saving new schema version")
        schema = orm.SchemaVersion(
            map_definition = map_definition,
            map_owner = map_owner
        )
        self.session.add(map_definition)
        self.schema = schema
        
        # Map Instance
        self.logger.info("Saving map instance")
        map_instance = orm.MapInstance(
            schema = schema,
            map_definition = map_definition,
            retrieval_date = datetime.now(),
            source_path = 'data/%s' % self.file_name,
        )
        self.map_instance = map_instance
        
        # Schema Fields
        self.logger.info("Saving schema fields")
        for field, field_meta in map_config.get('schema', {}).items():
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
        

# Run ETL process

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest="input_file", default=None, help="Path to a job file to process", metavar="input")

    results = parser.parse_args()
    
    TM = TransforMap(results.input_file)
    TM.fetch_http()
    TM.transform_data()
    TM.save_map()


    