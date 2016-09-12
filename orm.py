#!/usr/bin/env python
# coding: utf-8

from sqlalchemy import create_engine, UniqueConstraint
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Numeric, \
    Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from ConfigParser import SafeConfigParser

config = SafeConfigParser()
config.read('transformap.conf')

Base = declarative_base()

def db_connect():
    
    user = config.get('database', 'username')
    name = config.get('database', 'name')
    password = config.get('database', 'password')
    host = config.get('database', 'host')
    port = 3306
    
    engine = create_engine(
        'mysql://%s:%s@%s:%s/%s?charset=utf8' %
        (user, password, host, port, name), echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Create tables if they don't exist
    Base.metadata.create_all(engine)
    
    return session
 
class MapOwner(Base, object):
    __tablename__ = 'map_owners'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    
class MapDefinition(Base, object):
    __tablename__ = 'map_definitions'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    owner_id = Column(Integer, ForeignKey('map_owners.id'), nullable=False)
    owner = relationship('MapOwner')
    
class SchemaVersion(Base, object):
    __tablename__ = 'schema_versions'
    id = Column(Integer, primary_key=True)
    map_definition_id = Column(Integer, ForeignKey('map_definitions.id'), nullable=False)
    map_owner_id = Column(Integer, ForeignKey('map_owners.id'), nullable=False)
    map_definition = relationship('MapDefinition')
    map_owner = relationship('MapOwner')
    
class SchemaField(Base, object):
    __tablename__ = 'schema_fields'
    id = Column(Integer, primary_key=True)
    is_base_field = Column(Boolean, default=False)
    schema_id = Column(Integer, ForeignKey('schema_versions.id'), nullable=False)
    schema = relationship('SchemaVersion')
    field_name = Column(String(255))
    field_type = Column(String(255))
    field_description = Column(Text)
    
class MapInstance(Base, object):
    __tablename__ = 'map_instances'
    id = Column(Integer, primary_key=True)
    schema_id = Column(Integer, ForeignKey('schema_versions.id'), nullable=False)
    schema = relationship('SchemaVersion')
    map_definition_id = Column(Integer, ForeignKey('map_definitions.id'), nullable=False)
    map_definition = relationship('MapDefinition')
    retrieval_date = Column(DateTime)
    source_path = Column(String(255))
    
class MapObject(Base, object):
    __tablename__ = 'map_object'
    id = Column(Integer, primary_key=True)
    guid = Column(Integer)
    map_instance_id = Column(Integer, ForeignKey('map_instances.id'), nullable=False)
    map_instance = relationship('MapInstance')
    longitude = Column(Numeric(14,10))
    latitude = Column(Numeric(14,10))
    
class MapData(Base, object):
    __tablename__ = 'map_data'
    id = Column(Integer, primary_key=True)
    map_instance_id = Column(Integer, ForeignKey('map_instances.id'), nullable=False)
    map_instance = relationship('MapInstance')
    map_object_id = Column(Integer, ForeignKey('map_object.id'), nullable=False)
    map_object = relationship('MapObject')
    schema_field_id = Column(Integer, ForeignKey('schema_fields.id'), nullable=False)
    schema_field = relationship('SchemaField')
    field_value = Column(String(255, collation='utf8_bin'))
    
    __table_args__ =  (UniqueConstraint('map_instance_id', 'map_object_id', 'schema_field_id',  name='uix_1'),)