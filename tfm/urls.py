from django.conf.urls import url, include
from django.contrib import admin

import places.api, places.views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^places-api/', include(places.api.router.urls)),
    url(r'^map-instance/(?P<map_instance_id>\d+)/$', places.views.map_instance_geojson)
]
