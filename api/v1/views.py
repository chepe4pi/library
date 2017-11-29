from rest_framework import viewsets
from .serializers import AuthorSerializer, BookSerializer, ExpandedBookSerializer, CategorySerializer
from catalog.models import Author, Book, Category


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()

    def get_serializer_class(self):
        if self.request.GET.get('expand', False):
            return ExpandedBookSerializer

        return BookSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
