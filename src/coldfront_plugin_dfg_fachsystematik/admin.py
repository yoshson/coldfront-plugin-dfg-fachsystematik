"""Django admin registration for the DFG Fachsystematik plugin (ColdFront 2.x).

ColdFront 2.x still ships ``django.contrib.admin``; the plugin exposes its
models there for low-level housekeeping. The primary integration runs
through the plugin API (menu, project tab, assignment views).
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import DfgSubject, ProjectSubjectAssignment


@admin.register(DfgSubject)
class DfgSubjectAdmin(admin.ModelAdmin):
    """Browse and manage the imported DFG subjects."""

    list_display = (
        "number",
        "name_en",
        "name_de",
        "board",
        "area",
        "discipline",
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
        "discipline_name_en",
        "discipline_name_de",
    )
    list_filter = (
        "discipline_number",
        "area_number",
    )
    ordering = ("number",)

    @admin.display(description=_("Review board (Fachkollegium)"))
    def board(self, obj):
        return f"{obj.board_number} {obj.board_name_en}"

    @admin.display(description=_("Subject area (Fachgebiet)"))
    def area(self, obj):
        return f"{obj.area_number} {obj.area_name_en}"

    @admin.display(description=_("Scientific discipline (Wissenschaftsbereich)"))
    def discipline(self, obj):
        return f"{obj.discipline_number} {obj.discipline_name_en}"


@admin.register(ProjectSubjectAssignment)
class ProjectSubjectAssignmentAdmin(admin.ModelAdmin):
    """Browse and manage project subject assignments."""

    list_display = (
        "project",
        "subject",
        "created",
        "last_updated",
    )
    search_fields = (
        "project__name",
        "subject__number",
        "subject__name_en",
        "subject__name_de",
    )
    # ras.Project has no Django admin registration in 2.x, so the project
    # is picked via raw id; subjects resolve through this plugin's admin.
    raw_id_fields = ("project",)
    autocomplete_fields = ("subject",)
