from django.conf.urls import url, include

urlpatterns = [
    url(r'^v1/', include('api.v1.urls', namespace='v1')),
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
]
