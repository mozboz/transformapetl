#!/usr/bin/env python
# coding: utf-8

from datetime import datetime
from job import TMJob


class Load(TMJob):
        
    def __init__(self, config):
        self.setup_logging('Loader')
        super(Load, self).__init__(config)
        
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
        schema = self.session.query(self.orm.SchemaField).filter_by(schema_id=new_map['map_schema'].id).all()
        for schema_field in schema:
            field_name = schema_field.field_name
            field_id = schema_field.id
            map_schema[field_name] = field_id
            
        # Save data to db
        self.logger.info("Saving map data to database")
        for row in map_data:
            
            # save map object
            map_object = self.orm.MapObject(
                longitude = row.get('longitude'),
                latitude = row.get('latitude'),
                map_instance = new_map['map_instance'],
            )
            self.session.add(map_object)
            self.session.commit()
            
            # save new rows for object
            for field, value in row.items():
                if field not in ('latitude', 'longitude'):            
                    new_row = self.orm.MapData(
                        map_instance = new_map['map_instance'],
                        map_object = map_object,
                        schema_field_id = map_schema[field],
                        field_value = value,
                    )
                    self.session.add(new_row)
                    self.session.commit()
                    
        return True
        
    def initialise_map(self, file_name, map_config):

        ''' 
        Save new map instance metadata to database as needed.
        '''
        
        # Map Owner (if necessary)
        map_owner = self.session.query(self.orm.MapOwner).filter_by(name=map_config.get('owner')).first()
        
        if not map_owner:
            self.logger.info("Saving new map owner %s" % map_config.get('owner'))
            map_owner = self.orm.MapOwner(name=map_config.get('owner'))
            self.session.add(map_owner)
            
        # Map Definition (if necessary)
        map_definition = self.session.query(self.orm.MapDefinition).filter_by(name=map_config.get('definition')).first()
        
        if not map_definition:
            self.logger.info("Saving new map definition %s" % map_config.get('definition'))
            map_definition = self.orm.MapDefinition(
                name=map_config.get('definition'),
                owner=map_owner,
            )
            self.session.add(map_definition)
            
        # Schema Version
        self.logger.info("Saving schema version")
        schema = self.orm.SchemaVersion(
            map_definition = map_definition,
            map_owner = map_owner
        )
        self.session.add(map_definition)
        
        # Map Instance
        self.logger.info("Saving map instance")
        map_instance = self.orm.MapInstance(
            schema = schema,
            map_definition = map_definition,
            retrieval_date = datetime.now(),
            source_path = 'data/%s' % file_name,
        )
        
        # Schema Fields
        self.logger.info("Saving schema fields")
        for field, field_meta in map_config.get('schema').items():

            new_field = self.orm.SchemaField(
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
            