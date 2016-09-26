from django.conf.urls import url, include
from django.contrib import admin

import places.api


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^places-api/', include(places.api.router.urls)),
]
