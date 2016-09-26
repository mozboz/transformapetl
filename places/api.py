from places.models import MapOwner, MapInstance, MapObject, MapData, \
    MapDefinition, SchemaField, SchemaVersion

from rest_framework import filters, routers, serializers, viewsets



class OwnerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MapOwner
        fields = ('name', 'date_added', 'date_modified')


class OwnerViewSet(viewsets.ModelViewSet):
    queryset = MapOwner.objects.all()
    serializer_class = OwnerSerializer


router = routers.DefaultRouter()
router.register('map_owners', OwnerViewSet)

