from django.conf.urls import url
from rest_framework import routers
from .views import AuthorViewSet, BookViewSet, CategoryViewSet
from django.conf.urls import include

router = routers.SimpleRouter()
router.register(r'authors', AuthorViewSet)
router.register(r'books', BookViewSet)
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    url(r'', include(router.urls))
]
