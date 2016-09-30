#!/usr/bin/env python
# coding: utf-8

from _jobs import TMJob

from places.models import MapData, MapDefinition, MapInstance, \
    MapObject, MapOwner, SchemaField, SchemaVersion

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
        return True

    def save_map(self, new_map, map_data):

        '''
        Save data to database.
        '''

        # Fetch schema for this map instance from DB
        map_schema = {}
        schema = SchemaField.objects.filter(schema_id = new_map['map_schema'])
        
        for schema_field in schema:
            field_name = schema_field.field_name
            field_id = schema_field.id
            map_schema[field_name] = schema_field
            
        # Save data to db
        self.logger.info("Saving map data to database")
        for row in map_data:
        
            # save map object
            map_object = MapObject(
                longitude = row.get('longitude'),
                latitude = row.get('latitude'),
                map_instance = new_map['map_instance'],
            )
            map_object.save()
            
            # save new rows for object
            for field, value in row.items():
                if field not in ('latitude', 'longitude'):
                              
                    new_row = MapData(
                        map_instance = new_map['map_instance'],
                        map_object = map_object,
                        schema_field = map_schema[field],
                        field_value = value,
                    )
                    new_row.save()
        
    def initialise_map(self, file_name, map_config):

        ''' 
        Save new map instance metadata to database as needed.
        '''
        
        # Map Owner (if necessary)
        map_owner = MapOwner.objects.filter(name=map_config.get('owner')).first()
        
        if not map_owner:
            self.logger.info("Saving new map owner %s" % map_config.get('owner'))
            map_owner = MapOwner(name=map_config.get('owner'))
            map_owner.save()
            
        # Map Definition (if necessary)
        map_definition = MapDefinition.objects.filter(name=map_config.get('definition')).first()
        
        if not map_definition:
            self.logger.info("Saving new map definition %s" % map_config.get('definition'))
            map_definition = MapDefinition(
                name=map_config.get('definition'),
                owner=map_owner,
            )
            map_definition.save()
            
        # Schema Version
        self.logger.info("Saving schema version")
        schema = SchemaVersion(
            map_definition = map_definition,
            map_owner = map_owner
        )
        schema.save()
        
        # Map Instance
        self.logger.info("Saving map instance")
        map_instance = MapInstance(
            schema = schema,
            map_definition = map_definition,
            source_path = 'data/%s' % file_name,
        )
        map_instance.save()
        
        # Schema Fields
        self.logger.info("Saving schema fields")
        for field, field_meta in map_config.get('schema').items():

            new_field = SchemaField(
                is_base_field = False,
                schema = schema,
                field_name = field_meta.get('target_field_name'),
                field_type = field_meta.get('type'),
                field_description = field_meta.get('description'),
            )
            new_field.save()
        
        return {
            'map_instance' : map_instance,
            'map_schema' : schema,
        }
            