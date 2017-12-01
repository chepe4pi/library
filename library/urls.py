from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^rest-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/', include('api.urls', namespace='api')),
    url(r'^', include('catalog.urls'))
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
