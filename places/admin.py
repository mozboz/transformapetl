from django.contrib import admin

from places.models import MapOwner, MapInstance, MapObject, MapData, \
    MapDefinition, SchemaField, SchemaVersion
    
    
     
class MapObjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'map_instance', 'longitude', 'latitude', 'date_created')
    list_display_links = ('id', )
    

class MapInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'schema', 'map_definition', 'date_created')
    list_display_links = ('id',)
    
    
class MapOwnerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_created',)
    list_display_links = ('id',)
    

class MapDefinitionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'date_created')
    list_display_links = ('id',)


class SchemaFieldAdmin(admin.ModelAdmin):
    list_display = ('id', 'schema', 'field_name', 'field_type')
    list_display_links = ('id',)


class SchemaVersionAdmin(admin.ModelAdmin):
    list_display = ('id', 'map_definition', 'map_owner', 'date_created')
    list_display_links = ('id',)


class MapDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'map_instance', 'map_object', 'schema_field')
    list_display_links = ('id',)



admin.site.register(MapObject, MapObjectAdmin)
admin.site.register(MapInstance, MapInstanceAdmin)
admin.site.register(MapOwner, MapOwnerAdmin)
admin.site.register(MapDefinition, MapDefinitionAdmin)
admin.site.register(SchemaField, SchemaFieldAdmin)
admin.site.register(SchemaVersion, SchemaVersionAdmin)
admin.site.register(MapData, MapDataAdmin)

