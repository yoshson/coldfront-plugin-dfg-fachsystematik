"""FilterSets for the DFG Fachsystematik plugin (ColdFront 2.x)."""

import django_filters
from coldfront.lib.views.filtersets import ChangeLoggedModelFilterSet
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from .models import DfgSubject


class DfgSubjectFilterSet(ChangeLoggedModelFilterSet):
    q = django_filters.CharFilter(
        method="search",
        label=_("Search"),
    )
    board_number = django_filters.CharFilter(
        label=_("Review board (Fachkollegium) number"),
    )
    area_number = django_filters.CharFilter(
        label=_("Subject area (Fachgebiet) number"),
    )
    discipline_number = django_filters.CharFilter(
        label=_("Scientific discipline (Wissenschaftsbereich) number"),
    )

    class Meta:
        model = DfgSubject
        fields = (
            "board_number",
            "area_number",
            "discipline_number",
        )

    def search(self, queryset, name, value):
        """Bilingual search over numbers and names at all levels."""
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(number__icontains=value)
            | Q(name_en__icontains=value)
            | Q(name_de__icontains=value)
            | Q(board_name_en__icontains=value)
            | Q(board_name_de__icontains=value)
            | Q(area_name_en__icontains=value)
            | Q(area_name_de__icontains=value)
            | Q(discipline_name_en__icontains=value)
            | Q(discipline_name_de__icontains=value)
        ).distinct()
