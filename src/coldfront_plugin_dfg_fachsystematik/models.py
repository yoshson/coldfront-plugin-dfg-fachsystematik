"""Database models for the DFG Fachsystematik plugin (ColdFront 2.x).

ColdFront 2.x no longer ships a ``FieldOfScience`` concept, so the plugin
owns the classification data end to end:

``DfgSubject``
    One of the 214 subjects (Fächer) of the DFG Fachsystematik, carrying the
    numbers and names of the review board (Fachkollegium), subject area
    (Fachgebiet) and scientific discipline (Wissenschaftsbereich) above it
    as denormalized columns. Sourced from the same bilingual CSV used by the
    DFG-Fachsystematik-Ontology project
    (https://github.com/tibonto/DFG-Fachsystematik-Ontology).

``ProjectSubjectAssignment``
    Links a ``ras.Project`` to the subject that best describes it. One
    subject per project, mirroring the 1.x plugin's single
    ``field_of_science`` foreign key.

Both models derive from ``ColdFrontModel`` and therefore support change
logging, tags, custom fields and cloning out of the box.

Reference: https://www.dfg.de/en/dfg_profile/statutory_bodies/review_boards/
"""

from typing import ClassVar

from coldfront.lib.models import ColdFrontModel
from django.db import models
from django.utils.translation import gettext_lazy as _


class DfgSubject(ColdFrontModel):
    """A subject (Fach) of the DFG Fachsystematik with its full ancestry."""

    number = models.CharField(
        max_length=10,
        unique=True,
        verbose_name=_("subject number"),
        help_text=_("Official DFG subject number (Fachnummer), e.g. '111-01'."),
    )
    name_en = models.CharField(
        max_length=255,
        verbose_name=_("name (English)"),
        help_text=_("Official English subject name (Fach)."),
    )
    name_de = models.CharField(
        max_length=255,
        verbose_name=_("name (German)"),
        help_text=_("Official German subject name (Fach)."),
    )
    board_number = models.CharField(
        max_length=10,
        verbose_name=_("review board number"),
        help_text=_("DFG number of the review board (Fachkollegium), e.g. '213'."),
    )
    board_name_en = models.CharField(
        max_length=255,
        verbose_name=_("review board (English)"),
        help_text=_("English name of the review board (Fachkollegium)."),
    )
    board_name_de = models.CharField(
        max_length=255,
        verbose_name=_("review board (German)"),
        help_text=_("German name of the review board (Fachkollegium)."),
    )
    area_number = models.CharField(
        max_length=10,
        verbose_name=_("subject area number"),
        help_text=_("DFG number of the subject area (Fachgebiet), e.g. '21'."),
    )
    area_name_en = models.CharField(
        max_length=255,
        verbose_name=_("subject area (English)"),
        help_text=_("English name of the subject area (Fachgebiet)."),
    )
    area_name_de = models.CharField(
        max_length=255,
        verbose_name=_("subject area (German)"),
        help_text=_("German name of the subject area (Fachgebiet)."),
    )
    discipline_number = models.CharField(
        max_length=10,
        verbose_name=_("scientific discipline number"),
        help_text=_(
            "DFG number of the scientific discipline (Wissenschaftsbereich), e.g. '2'."
        ),
    )
    discipline_name_en = models.CharField(
        max_length=255,
        verbose_name=_("scientific discipline (English)"),
        help_text=_(
            "English name of the scientific discipline (Wissenschaftsbereich)."
        ),
    )
    discipline_name_de = models.CharField(
        max_length=255,
        verbose_name=_("scientific discipline (German)"),
        help_text=_("German name of the scientific discipline (Wissenschaftsbereich)."),
    )

    class Meta:
        ordering: ClassVar[list[str]] = ["number"]
        verbose_name = _("DFG subject (Fach)")
        verbose_name_plural = _("DFG subjects (Fächer)")

    def __str__(self):
        return f"{self.number} {self.name_en}"

    @property
    def full_label(self):
        """Full path label, e.g. '2 Biology › 21 … › 213 … › 213-01 …'."""
        return " › ".join(
            [
                f"{self.discipline_number} {self.discipline_name_en}",
                f"{self.area_number} {self.area_name_en}",
                f"{self.board_number} {self.board_name_en}",
                f"{self.number} {self.name_en}",
            ]
        )


class ProjectSubjectAssignment(ColdFrontModel):
    """The DFG subject assigned to a project."""

    project = models.OneToOneField(
        to="ras.Project",
        on_delete=models.CASCADE,
        related_name="dfg_subject_assignment",
        verbose_name=_("project"),
        help_text=_("The project this subject is assigned to."),
    )
    subject = models.ForeignKey(
        to=DfgSubject,
        on_delete=models.PROTECT,
        related_name="assignments",
        verbose_name=_("subject (Fach)"),
        help_text=_("The subject that best describes this project."),
    )

    class Meta:
        ordering: ClassVar[list[str]] = ["project__name"]
        verbose_name = _("project subject assignment")
        verbose_name_plural = _("project subject assignments")

    def __str__(self):
        return f"{self.project}: {self.subject}"
