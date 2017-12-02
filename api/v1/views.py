from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import AuthorSerializer, BookSerializer, ExpandedBookSerializer, CategorySerializer, \
    BookmarkSerializer, ExpandedBookmarkSerializer, StaffBookmarkSerializer, BookRatingSerializer, \
    ExpandedBookRatingSerializer, StaffBookRatingSerializer
from catalog.models import Author, Book, Category, Bookmark, BookRating
from .filter_backends import BookmarkFilter, StaffAccessFilter, BookRatingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .mixins.views import ExpandableViewSetMixin, PrefetchUserData, StaffViewSetMixin


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class BookViewSet(ExpandableViewSetMixin, PrefetchUserData, viewsets.ModelViewSet):
    queryset = Book.objects.all().prefetch_related('categories').select_related('author')
    serializer_class = BookSerializer
    serializer_expanded_class = ExpandedBookSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BookmarkViewSet(StaffViewSetMixin, ExpandableViewSetMixin, PrefetchUserData, viewsets.ModelViewSet):
    serializer_class = BookmarkSerializer
    serializer_expanded_class = ExpandedBookmarkSerializer
    staff_serializer_class = StaffBookmarkSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, StaffAccessFilter)
    filter_class = BookmarkFilter

    queryset = Bookmark.objects.all().select_related(
        'book', 'book__author'
    ).prefetch_related(
        'book__categories'
    )


class BookRatingViewSet(StaffViewSetMixin, ExpandableViewSetMixin, PrefetchUserData, viewsets.ModelViewSet):
    serializer_class = BookRatingSerializer
    serializer_expanded_class = ExpandedBookRatingSerializer
    staff_serializer_class = StaffBookRatingSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, StaffAccessFilter)
    filter_class = BookRatingFilter

    queryset = BookRating.objects.all()
