from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import AuthorSerializer, BookSerializer, ExpandedBookSerializer, CategorySerializer, \
    BookmarkSerializer, ExpandedBookmarkSerializer, StaffBookmarkSerializer
from catalog.models import Author, Book, Category, Bookmark
from .filters import BookmarkFilter
from django_filters.rest_framework import DjangoFilterBackend


class ExpandableViewSetMixin(viewsets.GenericViewSet):
    serializer_expanded_class = None

    def get_serializer_class(self):
        if self.request.GET.get('expand', False):
            return self.serializer_expanded_class
        return super().get_serializer_class()


class StaffViewSetMixin(viewsets.GenericViewSet):
    staff_serializer_class = None

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return self.staff_serializer_class
        return super().get_serializer_class()


class PrefetchBookmarksMixin(viewsets.GenericViewSet):
    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['bookmarked_books'] = []
        if self.request.user.pk:
            ctx['bookmarked_books'] = Bookmark.objects.filter(user=self.request.user).values_list('book__id', flat=True)
        return ctx


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
