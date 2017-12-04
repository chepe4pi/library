from rest_framework import viewsets
from catalog.models import UserBookRelation


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
            'user_book_relations': []
        })
        if self.request.user.pk:
            context.update({
                'user_book_relations': UserBookRelation.objects.filter(user=self.request.user)
                    .values_list('book__id', 'user__id', 'in_bookmarks', 'in_wishlist', 'rating')
            })
        return context
