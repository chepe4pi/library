from rest_framework.filters import BaseFilterBackend
from django.db.models import QuerySet, Model


class UserAccessRestrictionFilterBackend(BaseFilterBackend):
    user_field_name = 'user'

    def filter_queryset(self, request, queryset, view):
        user = self.get_user(request)
        assert hasattr(queryset.model, self.user_field_name), "Model being filtered is not associated with a user"

        if self.should_restrict_access(user):
            return self.get_restricted_queryset(queryset, user)

        return queryset

    def should_restrict_access(self, user):
        return not user.is_staff

    def get_user(self, request):
        return request.user

    def get_restricted_queryset(self, queryset, user):
        return queryset.filter(**{self.user_field_name: user})
