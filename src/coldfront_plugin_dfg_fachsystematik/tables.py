"""django-tables2 tables for the DFG Fachsystematik plugin (ColdFront 2.x)."""

import django_tables2 as tables
from coldfront.lib.tables import ColdFrontTable
from django.utils.translation import gettext_lazy as _

from .models import DfgSubject


class DfgSubjectTable(ColdFrontTable):
    number = tables.Column(
        verbose_name=_("Number"),
        linkify=True,
    )
    name_en = tables.Column(verbose_name=_("Name (English)"))
    name_de = tables.Column(verbose_name=_("Name (German)"))
    board = tables.Column(
        verbose_name=_("Review board (Fachkollegium)"),
        accessor="board_name_en",
        linkify=False,
    )

    class Meta(ColdFrontTable.Meta):
        model = DfgSubject
        fields = (
            "pk",
            "id",
            "number",
            "name_en",
            "name_de",
            "board",
            "actions",
        )

    def render_board(self, record):
        return f"{record.board_number} {record.board_name_en} · {record.board_name_de}"
