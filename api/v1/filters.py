from rest_framework.filters import BaseFilterBackend
from django.db.models import QuerySet, Model


class UserAccessRestrictionFilterBackend(BaseFilterBackend):
    user_field_name = 'user'

    def filter_queryset(self, request, queryset, view):
        user = request.user
        if not user.is_staff:
            return queryset.filter(user=user)
        return queryset
