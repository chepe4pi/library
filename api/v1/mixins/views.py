from rest_framework import viewsets


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
        context.update({})
        if self.request.user.pk:
            context.update({})
        return context
