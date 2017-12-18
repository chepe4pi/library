from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import AuthorSerializer, BookSerializer, ExpandedBookSerializer, CategorySerializer, \
    UserBookRelationSerializer, ExpandedUserBookRelationSerializer, StaffBookRelationSerializer
from catalog.models import Author, Book, Category
from .filter_backends import StaffAccessFilter, UserBookRelationFilter
from django_filters.rest_framework import DjangoFilterBackend
from .mixins.views import ExpandableViewSetMixin, PrefetchUserData, StaffViewSetMixin
from catalog.models import UserBookRelation


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class BookViewSet(ExpandableViewSetMixin, PrefetchUserData, viewsets.ModelViewSet):
    queryset = Book.objects.select_related('author')
    serializer_class = BookSerializer
    serializer_expanded_class = ExpandedBookSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.should_expand():
            queryset = queryset.prefetch_related('categories')
        return queryset


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class UserBookRelationViewSet(ExpandableViewSetMixin, PrefetchUserData, StaffViewSetMixin, viewsets.ModelViewSet):
    serializer_class = UserBookRelationSerializer
    serializer_expanded_class = ExpandedUserBookRelationSerializer
    staff_serializer_class = StaffBookRelationSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, StaffAccessFilter,)
    filter_class = UserBookRelationFilter
    queryset = UserBookRelation.objects.all()


class ExpandedBookRelationViewSet(UserBookRelationViewSet):
    book = BookSerializer(read_only=True)
