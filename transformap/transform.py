#!/usr/bin/env python
# coding: utf-8

import urllib
import json

from job import TMJob


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
        
        
class TransformGeojson(Transform):       
        
    def run(self, extractor_response):

        '''
        Transform .GEOJSON map data in file according to schema.
        '''

        file_name = extractor_response.get('file_name')
        data = self.open_file(file_name)
        schema = self.schema_dict()
    
        self.logger.info("Transforming data according to schema")
        
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
        
        # response
        return {
            'map_data' : transformed_data,
            'file_name' : file_name,
            'map_schema' : schema,
        }