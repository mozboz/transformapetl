#!/usr/bin/env python
# coding: utf-8

import urllib
import json

from _jobs import Transform


class TransformDatagovGeojson(Transform):       
        
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
                'longitude' : '{0:.10f}'.format(row.get('geometry', {}).get('coordinates', {})[0]),
                'latitude' : '{0:.10f}'.format(row.get('geometry', {}).get('coordinates', {})[1]),
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


class TransformConvergirJson(Transform):       
        
    def run(self, extractor_response):

        '''
        Transform Convergir .JSON map file in file according to schema.
        '''

        file_name = extractor_response.get('file_name')
        data = self.open_file(file_name)
        schema = self.schema_dict()
    
        self.logger.info("Transforming data according to schema")
        
        transformed_data = []
        
        # Transform each row
        for row in data:

            new_row = {
                'longitude' : '{0:.10f}'.format(row.get('coordinates', {})[1]),
                'latitude' : '{0:.10f}'.format(row.get('coordinates', {})[0]),
            }
            
            for field, value in row.items():

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

        
class TransformOsmJson(Transform):       
        
    def run(self, extractor_response):

        '''
        Transform Convergir .JSON map file in file according to schema.
        '''

        file_name = extractor_response.get('file_name')
        data = self.open_file(file_name)
        schema = self.schema_dict()
    
        self.logger.info("Transforming data according to schema")
        
        transformed_data = []

        # Transform each row
        for row in data.get('elements', []):
        
            # dont' save objects without coordinates
            if not row.get('lon') or not row.get('lat'):
                continue

            new_row = {
                'longitude' : row.get('lon'),
                'latitude' : row.get('lat'),
            }
            
            for field, value in row.get('tags', {}).items():

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