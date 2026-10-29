"""Django admin integration for the DFG Fachsystematik plugin.

``DfgSubjectAdmin`` is the plugin's own admin section, registered normally
via autodiscovery. ``DfgFieldOfScienceAdmin`` replaces ColdFront's plain
``FieldOfScienceAdmin``; it is *not* registered here, but by
``patch.apply_patches``, so that replacing a ColdFront admin stays behind
the ``DFG_FACHSYSTEMATIK_PATCH_PROJECT_FORM`` setting.
"""

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import DfgSubject


@admin.register(DfgSubject)
class DfgSubjectAdmin(admin.ModelAdmin):
    """Browse the DFG metadata of the imported fields of science."""

    list_display = (
        "number",
        "name_en",
        "name_de",
        "board",
        "field_of_science_link",
    )
    search_fields = (
        "number",
        "name_en",
        "name_de",
        "board_number",
        "board_name_en",
        "board_name_de",
        "area_name_en",
        "area_name_de",
        "field_of_science__description",
    )
    list_filter = (
        "discipline_number",
        "area_number",
    )
    ordering = ("number",)

    @admin.display(description="Review board (Fachkollegium)")
    def board(self, obj):
        return f"{obj.board_number} {obj.board_name_en}"

    @admin.display(description="Field of science")
    def field_of_science_link(self, obj):
        url = reverse(
            "admin:field_of_science_fieldofscience_change",
            args=[obj.field_of_science_id],
        )
        return format_html('<a href="{}">{}</a>', url, obj.field_of_science.description)


class DfgFieldOfScienceAdmin(admin.ModelAdmin):
    """DFG-aware replacement for ColdFront's ``FieldOfScienceAdmin``.

    The list view gains the parent (Fachkollegium level is not stored as
    rows, so typically empty) and a link to the row's ``DfgSubject``
    metadata; the search also matches DFG numbers and German names. The
    canonical ``"<Fachnummer> <English name>"`` descriptions of DFG rows
    are read-only — the importer enforces them on every load, so manual
    edits would silently be reverted. NSF rows stay editable as before.

    Registered by ``patch.apply_patches`` (not via ``@admin.register``)
    because replacing a ColdFront admin is part of the optional
    integration.
    """

    list_display = (
        "description",
        "is_selectable",
        "parent_description",
        "dfg_subject_link",
    )
    list_filter = ("is_selectable",)
    list_select_related = ("parent_id", "dfg_subject")
    search_fields = (
        "description",
        "dfg_subject__number",
        "dfg_subject__name_en",
        "dfg_subject__name_de",
    )

    @admin.display(description="Parent")
    def parent_description(self, obj):
        # The core FK attribute is literally named parent_id, so the raw
        # column is parent_id_id and obj.parent_id holds the related row.
        parent = obj.parent_id
        return parent.description if parent is not None else "—"

    @admin.display(description="DFG subject (Fach)")
    def dfg_subject_link(self, obj):
        dfg_subject = getattr(obj, "dfg_subject", None)
        if dfg_subject is None:
            return "—"
        url = reverse(
            "admin:dfg_fachsystematik_dfgsubject_change",
            args=[dfg_subject.pk],
        )
        return format_html('<a href="{}">{}</a>', url, dfg_subject.number)

    def get_readonly_fields(self, request, obj=None):
        readonly = super().get_readonly_fields(request, obj)
        if obj is not None and getattr(obj, "dfg_subject", None) is not None:
            return (*readonly, "description")
        return readonly
