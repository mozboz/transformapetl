from places.models import MapOwner, MapInstance, MapObject, MapData, \
    MapDefinition, SchemaField, SchemaVersion

from rest_framework import filters, routers, serializers, viewsets


# Map Owner

class MapOwnerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MapOwner
        fields = ('name', 'date_created', 'date_modified')

class MapOwnerViewSet(viewsets.ModelViewSet):
    queryset = MapOwner.objects.all()
    serializer_class = MapOwnerSerializer
    


# Map Data

class MapDataSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MapData
        fields = ('map_instance', 'map_object', 'schema_field', 'field_value', 'date_created', 'date_modified')

class MapDataViewSet(viewsets.ModelViewSet):
    queryset = MapData.objects.all()
    serializer_class = MapDataSerializer
    


# Map Instance (lite)

class MapInstanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = MapInstance
        fields = ('id', 'schema', 'map_definition', 'date_created', 'date_modified',)

class MapInstanceViewSet(viewsets.ModelViewSet):
    queryset = MapInstance.objects.all()
    serializer_class = MapInstanceSerializer
    
    
# Map Instance (verbose)

class MapInstanceVerboseSerializer(serializers.ModelSerializer):

    class Meta:
        model = MapInstance
        depth = 2
        fields = ('id', 'schema', 'map_definition', 'date_created', 'date_modified', 'mapdata_set')

class MapInstanceVerboseViewSet(viewsets.ModelViewSet):
    queryset = MapInstance.objects.all()
    serializer_class = MapInstanceVerboseSerializer
    



# Map Object

class MapObjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MapObject
        fields = ('guid', 'map_instance', 'longitude', 'latitude', 'date_created', 'date_modified')

class MapObjectViewSet(viewsets.ModelViewSet):
    queryset = MapObject.objects.all()
    serializer_class = MapObjectSerializer

# Map Definition

class MapDefinitionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MapDefinition
        fields = ('name', 'owner', 'date_created', 'date_modified')

class MapDefinitionViewSet(viewsets.ModelViewSet):
    queryset = MapDefinition.objects.all()
    serializer_class = MapDefinitionSerializer

# Schema Field

class SchemaFieldSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SchemaField
        fields = ('is_base_field', 'schema', 'field_name', 'field_type', 'field_description', 'date_created', 'date_modified')

class SchemaFieldViewSet(viewsets.ModelViewSet):
    queryset = SchemaField.objects.all()
    serializer_class = SchemaFieldSerializer
    
# Schema Version

class SchemaVersionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SchemaVersion
        fields = ('map_definition', 'map_owner', 'date_created', 'date_modified')

class SchemaVersionViewSet(viewsets.ModelViewSet):
    queryset = SchemaVersion.objects.all()
    serializer_class = SchemaVersionSerializer




router = routers.DefaultRouter()

router.register('map_owners', MapOwnerViewSet)
router.register('map_instance', MapInstanceViewSet)
router.register('map_instance_verbose', MapInstanceVerboseViewSet)
router.register('map_object', MapObjectViewSet)
router.register('map_data', MapDataViewSet)
router.register('map_definition', MapDefinitionViewSet)
router.register('schema_field', SchemaFieldViewSet)
router.register('schema_version', SchemaVersionViewSet)

