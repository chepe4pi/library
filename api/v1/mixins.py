from rest_framework import viewsets
from catalog.models import Bookmark


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
