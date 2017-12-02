from django_filters.rest_framework import FilterSet
from rest_framework.filters import BaseFilterBackend
from catalog.models import Bookmark, BookRating


class BookmarkFilter(FilterSet):
    class Meta:
        model = Bookmark
        fields = ('book', 'user')


class BookRatingFilter(FilterSet):
    class Meta:
        model = BookRating
        fields = ('book', 'user', 'rating')


class StaffAccessFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if not request.user.is_staff:
            return queryset.filter(user=request.user)
        return queryset
