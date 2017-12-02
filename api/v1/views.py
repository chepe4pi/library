from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import AuthorSerializer, BookSerializer, ExpandedBookSerializer, CategorySerializer, \
    BookmarkSerializer, ExpandedBookmarkSerializer, StaffBookmarkSerializer
from catalog.models import Author, Book, Category, Bookmark
from .filter_backends import BookmarkFilter
from django_filters.rest_framework import DjangoFilterBackend
from .mixins import ExpandableViewSetMixin, PrefetchBookmarksMixin, StaffViewSetMixin


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class BookViewSet(ExpandableViewSetMixin, PrefetchBookmarksMixin, viewsets.ModelViewSet):
    queryset = Book.objects.all().prefetch_related('categories').select_related('author')
    serializer_class = BookSerializer
    serializer_expanded_class = ExpandedBookSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BookmarkViewSet(StaffViewSetMixin, ExpandableViewSetMixin, PrefetchBookmarksMixin, viewsets.ModelViewSet):
    serializer_class = BookmarkSerializer
    serializer_expanded_class = ExpandedBookmarkSerializer
    staff_serializer_class = StaffBookmarkSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = BookmarkFilter

    queryset = Bookmark.objects.all().select_related(
        'book', 'book__author'
    ).prefetch_related(
        'book__categories'
    )
