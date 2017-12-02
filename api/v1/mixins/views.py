from rest_framework import viewsets
from catalog.models import Bookmark, BookRating


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


class PrefetchUserData(viewsets.GenericViewSet):
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'bookmarked_books': [],
            'rated_books': []
        })
        if self.request.user.pk:
            context.update({
                'bookmarked_books': Bookmark.objects.filter(user=self.request.user).values_list('book__id', flat=True),
                'rated_books': BookRating.objects.filter(user=self.request.user).values_list('book__id', 'rating')
            })
        return context
