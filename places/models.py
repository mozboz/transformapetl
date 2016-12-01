# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

from __future__ import unicode_literals
from django.contrib.postgres.fields import JSONField

from django.db import models


class MapData(models.Model):
    map_instance = models.ForeignKey('MapInstance')
    map_object = models.ForeignKey('MapObject')
    schema_field = models.ForeignKey('SchemaField')
    field_value = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return u'%s' % self.field_value

    class Meta:
        db_table = 'map_data'
        unique_together = (('map_instance', 'map_object', 'schema_field'),)


class MapDefinition(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    owner = models.ForeignKey('MapOwner')
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        db_table = 'map_definitions'


class MapInstance(models.Model):
    schema = models.ForeignKey('SchemaVersion')
    map_definition = models.ForeignKey(MapDefinition)
    source_path = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return u'%s %s' % (self.map_definition, self.id)

    class Meta:
        db_table = 'map_instances'


class MapObject(models.Model):
    guid = models.IntegerField(blank=True, null=True)
    map_instance = models.ForeignKey(MapInstance)
    longitude = models.DecimalField(max_digits=14, decimal_places=10, blank=True, null=True)
    latitude = models.DecimalField(max_digits=14, decimal_places=10, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return u'%s %s' % (self.longitude, self.latitude)

    class Meta:
        db_table = 'map_object'


class MapOwner(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        db_table = 'map_owners'


class SchemaField(models.Model):
    is_base_field = models.IntegerField(blank=True, null=True)
    schema = models.ForeignKey('SchemaVersion')
    field_name = models.CharField(max_length=255, blank=True, null=True)
    field_type = models.CharField(max_length=255, blank=True, null=True)
    field_description = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return u'%s' % (self.field_name)

    class Meta:
        db_table = 'schema_fields'


class SchemaVersion(models.Model):
    map_definition = models.ForeignKey(MapDefinition)
    map_owner = models.ForeignKey(MapOwner)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return u'%s' % self.map_definition

    class Meta:
        db_table = 'schema_versions'

