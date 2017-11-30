from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import AuthorSerializer, BookSerializer, ExpandedBookSerializer, CategorySerializer, \
    BookmarkSerializer, ExpandedBookmarkSerializer, StaffBookmarkSerializer
from catalog.models import Author, Book, Category, Bookmark
from .filters import UserAccessRestrictionFilterBackend


class ExpandableViewSetMixin(viewsets.GenericViewSet):
    serializer_expanded_class = None

    def should_expand(self):
        return self.request.GET.get('expand', False)

    def get_serializer_class(self):
        if self.should_expand():
            return self.serializer_expanded_class

        return super().get_serializer_class()


class StaffViewSetMixin(viewsets.GenericViewSet):
    staff_serializer_class = None

    def get_serializer_class(self):
        if self.is_staff(self.get_user()):
            return self.staff_serializer_class

        return super().get_serializer_class()

    def get_user(self):
        return self.request.user

    def is_staff(self, user):
        return user.is_staff


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


class BookmarkViewSet(StaffViewSetMixin, ExpandableViewSetMixin, viewsets.ModelViewSet):
    serializer_class = BookmarkSerializer
    serializer_expanded_class = ExpandedBookmarkSerializer
    staff_serializer_class = StaffBookmarkSerializer
    queryset = Bookmark.objects.all()
    permission_classes = (IsAuthenticated,)
    filter_backends = (UserAccessRestrictionFilterBackend,)
