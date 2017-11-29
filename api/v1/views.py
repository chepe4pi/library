from rest_framework import viewsets
from .serializers import AuthorSerializer, BookSerializer, ExpandedBookSerializer, CategorySerializer
from catalog.models import Author, Book, Category


class ExpandableViewSetMixin(viewsets.ModelViewSet):
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
