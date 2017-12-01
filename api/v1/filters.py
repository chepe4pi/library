from django_filters.rest_framework import FilterSet
from catalog.models import Bookmark


class BookmarkFilter(FilterSet):
    @property
    def qs(self):
        qs = super().qs
        user = getattr(self.request, 'user', None)
        if user and not user.is_staff:
            qs = qs.filter(user=user.pk)
        return qs

    class Meta:
        model = Bookmark
        fields = ('book', 'user')
