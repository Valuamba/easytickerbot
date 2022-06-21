from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import ModelViewSet


class CustomOrderingFilter(OrderingFilter):
    def get_default_valid_fields(self, queryset, view, context={}):
        fields = super(CustomOrderingFilter, self).get_default_valid_fields(
            queryset, view, context
        )
        extra_fields = [
            (field, field) for field in getattr(view, "extra_ordering_fields", [])
        ]
        return fields + extra_fields


class CustomModelViewSet(ModelViewSet):
    filter_backends = [SearchFilter, CustomOrderingFilter]
