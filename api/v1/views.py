from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import detail_route, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .serializers import AuthorSerializer, BookSerializer, ExpandedBookSerializer, CategorySerializer, \
    BookmarkSerializer, ExpandedBookmarkSerializer
from catalog.models import Author, Book, Category, Bookmark


class ExpandableViewSetMixin(viewsets.GenericViewSet):
    serializer_expanded_class = None

    def should_expand(self):
        return self.request.GET.get('expand', False)

    def get_serializer_class(self):
        if self.should_expand():
            return self.serializer_expanded_class

        return super().get_serializer_class()


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class BookViewSet(ExpandableViewSetMixin, viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    serializer_expanded_class = ExpandedBookSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BookmarkViewSet(ExpandableViewSetMixin, viewsets.ModelViewSet):
    serializer_class = BookmarkSerializer
    serializer_expanded_class = ExpandedBookmarkSerializer
    queryset = Bookmark.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
