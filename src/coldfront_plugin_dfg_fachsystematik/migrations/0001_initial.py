"""Initial schema for the DFG Fachsystematik plugin."""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        # DfgSubject maps to coldfront's core FieldOfScience rows.
        ("field_of_science", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="DfgSubject",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "field_of_science",
                    models.OneToOneField(
                        help_text=(
                            "The ColdFront FieldOfScience row representing "
                            "this subject."
                        ),
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="dfg_subject",
                        to="field_of_science.fieldofscience",
                        verbose_name="field of science",
                    ),
                ),
                (
                    "number",
                    models.CharField(
                        help_text=(
                            "Official DFG subject number (Fachnummer), e.g. "
                            "'111-01'."
                        ),
                        max_length=10,
                        unique=True,
                    ),
                ),
                (
                    "name_en",
                    models.CharField(
                        help_text="Official English subject name (Fach).",
                        max_length=255,
                    ),
                ),
                (
                    "name_de",
                    models.CharField(
                        help_text="Official German subject name (Fach).",
                        max_length=255,
                    ),
                ),
                (
                    "board_number",
                    models.CharField(
                        help_text=(
                            "DFG number of the review board (Fachkollegium), "
                            "e.g. '111'."
                        ),
                        max_length=10,
                    ),
                ),
                (
                    "board_name_en",
                    models.CharField(
                        help_text=(
                            "English name of the review board (Fachkollegium)."
                        ),
                        max_length=255,
                    ),
                ),
                (
                    "board_name_de",
                    models.CharField(
                        help_text=(
                            "German name of the review board (Fachkollegium)."
                        ),
                        max_length=255,
                    ),
                ),
                (
                    "area_number",
                    models.CharField(
                        help_text=(
                            "DFG number of the subject area (Fachgebiet), "
                            "e.g. '11'."
                        ),
                        max_length=10,
                    ),
                ),
                (
                    "area_name_en",
                    models.CharField(
                        help_text=(
                            "English name of the subject area (Fachgebiet)."
                        ),
                        max_length=255,
                    ),
                ),
                (
                    "area_name_de",
                    models.CharField(
                        help_text=(
                            "German name of the subject area (Fachgebiet)."
                        ),
                        max_length=255,
                    ),
                ),
                (
                    "discipline_number",
                    models.CharField(
                        help_text=(
                            "DFG number of the scientific discipline "
                            "(Wissenschaftsbereich), e.g. '1'."
                        ),
                        max_length=10,
                    ),
                ),
                (
                    "discipline_name_en",
                    models.CharField(
                        help_text=(
                            "English name of the scientific discipline "
                            "(Wissenschaftsbereich)."
                        ),
                        max_length=255,
                    ),
                ),
                (
                    "discipline_name_de",
                    models.CharField(
                        help_text=(
                            "German name of the scientific discipline "
                            "(Wissenschaftsbereich)."
                        ),
                        max_length=255,
                    ),
                ),
            ],
            options={
                "verbose_name": "DFG subject (Fach)",
                "verbose_name_plural": "DFG subjects (Fächer)",
                "ordering": ["number"],
            },
        ),
    ]
