import django_filters

from ..models import Image


class ImageFilter(django_filters.FilterSet):
    """Filtros de listado; `is_reward_claimed` refleja `reward_claimed_at` (no es columna)."""

    is_reward_claimed = django_filters.BooleanFilter(method="filter_is_reward_claimed")

    class Meta:
        model = Image
        fields = ("device_type", "file_extension")

    def filter_is_reward_claimed(self, queryset, name, value):
        if value is True:
            return queryset.filter(reward_claimed_at__isnull=False)
        if value is False:
            return queryset.filter(reward_claimed_at__isnull=True)
        return queryset
