from urlparse import urlparse

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from places.models import MapInstance, MapData, MapObject

# Create your views here.

def map_instance_geojson(request, map_instance_id):

    '''
    Fetched all objects (and properties) for a given map instance, 
    returns a GEOJSON feature collection.
    '''
    
    # Fetch the map instance
    
    try:
        map_instance = MapInstance.objects.get(id=map_instance_id)
    except ObjectDoesNotExist:
        return JsonResponse({"Error" : "Map Instance with ID %s does not exist!" % map_instance_id})
    
    # Deduce URL from request
    
    request_url = urlparse(request.build_absolute_uri())
    base_url = 'http://%s%s' % (request_url.netloc, request_url.path)
    
    # Set pagination params
    
    page = int(request.GET.get('page', 1))
    x = (page - 1) * 25
    y = page * 25
    
    # Prepare GEOJSON response
    
    response = {
        "type"  : "Feature Collection",
        "count" : 25,
        "next"  : "%s?page=%s" % (base_url, page + 1),
    }
    
    if page <= 1:
        response['previous'] = None 
    else:
        response['previous'] = "%s?page=%s" % (base_url, page - 1)
        
    # Fetch and serialise map objects
    
    map_objects = MapObject.objects.filter(map_instance=map_instance).order_by('id')[x:y]
    
    features = []
    for map_object in map_objects:
        feature = {
            "type" : "Feature",
            "geometry" : {
                "type" : "Point",
                "coordinates": [
                    float(map_object.longitude),
                    float(map_object.latitude),
                ]
            },
            "properties" : {}
        }
        
        object_data = MapData.objects.filter(map_object=map_object)
        
        for field in object_data:
            field_name = field.schema_field
            feature["properties"][field.schema_field.field_name] = field.field_value
            
        features.append(feature)
        
    response['features'] = features

    return JsonResponse(response, safe=False)
    
    
    