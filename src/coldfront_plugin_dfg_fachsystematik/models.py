"""Database model linking DFG Fachsystematik subjects to ColdFront fields of science.

This plugin stores the classification itself in ColdFront's core
``FieldOfScience`` model: each of the 214 subjects (Fächer) of the DFG
Fachsystematik 2024–2028 becomes a ``FieldOfScience`` row whose
``description`` is ``"<Fachnummer> <English subject name>"`` (e.g.
``"111-01 Prehistory and World Archaeology"``). The subject selected at
project creation is therefore saved on the project's native
``field_of_science`` foreign key and is visible throughout ColdFront
(detail page, update form, search and reports) without any plugin glue.

``DfgSubject`` is the plugin's side table: it maps each such row back to its
DFG metadata — the official subject number, the German subject name, and
the numbers and names of the review board (Fachkollegium), subject area
(Fachgebiet) and scientific discipline (Wissenschaftsbereich) above it. It
powers the grouped, bilingual selection widget and keeps the hierarchy
queryable.

Reference: https://www.dfg.de/en/dfg_profile/statutory_bodies/review_boards/
subject_areas (data also used by the TIB DFG-Fachsystematik-Ontology project,
https://github.com/tibonto/DFG-Fachsystematik-Ontology).
"""

from typing import ClassVar

from django.db import models


class DfgSubject(models.Model):
    """DFG metadata for a ColdFront ``FieldOfScience`` row.

    Attributes:
        field_of_science (FieldOfScience): the core row this subject maps to
        number (str): official DFG subject number (Fachnummer), e.g. "111-01"
        name_en (str): official English subject name (Fach)
        name_de (str): official German subject name (Fach)
        board_number (str): DFG number of the review board (Fachkollegium)
        area_number (str): DFG number of the subject area (Fachgebiet)
        discipline_number (str): DFG number of the scientific discipline (Wissenschaftsbereich)
    """

    class Meta:
        ordering: ClassVar[list[str]] = ["number"]
        verbose_name = "DFG subject (Fach)"
        verbose_name_plural = "DFG subjects (Fächer)"

    field_of_science = models.OneToOneField(
        "field_of_science.FieldOfScience",
        on_delete=models.CASCADE,
        related_name="dfg_subject",
        verbose_name="field of science",
        help_text="The ColdFront FieldOfScience row representing this subject.",
    )
    number = models.CharField(
        max_length=10,
        unique=True,
        help_text="Official DFG subject number (Fachnummer), e.g. '111-01'.",
    )
    name_en = models.CharField(
        max_length=255,
        help_text="Official English subject name (Fach).",
    )
    name_de = models.CharField(
        max_length=255,
        help_text="Official German subject name (Fach).",
    )
    board_number = models.CharField(
        max_length=10,
        help_text="DFG number of the review board (Fachkollegium), e.g. '111'.",
    )
    board_name_en = models.CharField(
        max_length=255,
        help_text="English name of the review board (Fachkollegium).",
    )
    board_name_de = models.CharField(
        max_length=255,
        help_text="German name of the review board (Fachkollegium).",
    )
    area_number = models.CharField(
        max_length=10,
        help_text="DFG number of the subject area (Fachgebiet), e.g. '11'.",
    )
    area_name_en = models.CharField(
        max_length=255,
        help_text="English name of the subject area (Fachgebiet).",
    )
    area_name_de = models.CharField(
        max_length=255,
        help_text="German name of the subject area (Fachgebiet).",
    )
    discipline_number = models.CharField(
        max_length=10,
        help_text=(
            "DFG number of the scientific discipline (Wissenschaftsbereich), e.g. '1'."
        ),
    )
    discipline_name_en = models.CharField(
        max_length=255,
        help_text="English name of the scientific discipline (Wissenschaftsbereich).",
    )
    discipline_name_de = models.CharField(
        max_length=255,
        help_text="German name of the scientific discipline (Wissenschaftsbereich).",
    )

    def __str__(self):
        return f"{self.number} {self.name_en}"

    @property
    def full_label(self):
        """Full path label, e.g. '1 Life Sciences › 21 Biology › 213 Zoology › 213-01 …'."""
        return " › ".join(
            [
                f"{self.discipline_number} {self.discipline_name_en}",
                f"{self.area_number} {self.area_name_en}",
                f"{self.board_number} {self.board_name_en}",
                f"{self.number} {self.name_en}",
            ]
        )
