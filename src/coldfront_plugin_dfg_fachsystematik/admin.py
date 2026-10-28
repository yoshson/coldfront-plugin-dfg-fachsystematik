"""Django admin integration for the DFG Fachsystematik plugin."""

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
