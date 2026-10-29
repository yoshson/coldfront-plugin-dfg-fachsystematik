"""Import parsed Fachsystematik entries into ColdFront's field of science data.

Each DFG subject (Fach) becomes a row in ColdFront's core ``FieldOfScience``
model (the value stored on ``Project.field_of_science``), with the plugin's
``DfgSubject`` side table holding the DFG metadata.

The loader works with both the global Django app registry (management
command) and the historical registry passed into data migrations, so it must
only use ``apps.get_model(...)`` instead of importing models directly.
"""

from django.db import transaction

APP_LABEL = "dfg_fachsystematik"
FIELD_OF_SCIENCE_APP_LABEL = "field_of_science"


def subject_description(entry):
    """The FieldOfScience description for a DFG subject entry."""
    return f"{entry.number} {entry.subject_en}"


def _side_table_defaults(entry):
    return {
        "name_en": entry.subject_en,
        "name_de": entry.subject_de,
        "board_number": entry.review_board_number,
        "board_name_en": entry.review_board_en,
        "board_name_de": entry.review_board_de,
        "area_number": entry.subject_area_number,
        "area_name_en": entry.subject_area_en,
        "area_name_de": entry.subject_area_de,
        "discipline_number": entry.scientific_discipline_number,
        "discipline_name_en": entry.scientific_discipline_en,
        "discipline_name_de": entry.scientific_discipline_de,
    }


def import_fachsystematik(apps, entries):
    """Upsert the given ``FachsystematikEntry`` objects.

    For each subject:
    - the core ``FieldOfScience`` row gets the canonical description
      ``"<number> <English name>"`` and ``is_selectable=True``,
    - the ``DfgSubject`` side table entry (matched by DFG number) holds the
      bilingual names and the hierarchy.

    The import is idempotent and non-destructive: rows are updated in place;
    subjects absent from the CSV are kept in the database. The prepopulated
    NSF ``FieldOfScience`` rows are never touched except for the row behind
    ``FieldOfScience.DEFAULT_PK`` (kept in place and selectable, since new
    projects default to it).

    Returns a dict with per-model ``created``/``updated`` counters.
    """
    FieldOfScience = apps.get_model(FIELD_OF_SCIENCE_APP_LABEL, "FieldOfScience")
    DfgSubject = apps.get_model(APP_LABEL, "DfgSubject")

    stats = {
        model_name: {"created": 0, "updated": 0}
        for model_name in ("FieldOfScience", "DfgSubject")
    }

    with transaction.atomic():
        for entry in entries:
            description = subject_description(entry)
            defaults = _side_table_defaults(entry)

            dfg = (
                DfgSubject.objects.select_related("field_of_science")
                .filter(number=entry.number)
                .first()
            )
            if dfg is None:
                # New subject: get-or-create on the canonical description in
                # case the core row already exists (e.g. a previous import
                # whose side table was lost).
                fos, created = FieldOfScience.objects.get_or_create(
                    description=description,
                    defaults={"is_selectable": True},
                )
                stats["FieldOfScience"]["created" if created else "updated"] += 1
                DfgSubject.objects.create(
                    field_of_science=fos, number=entry.number, **defaults
                )
                stats["DfgSubject"]["created"] += 1
            else:
                # Existing subject: keep the core row's identity but enforce
                # the canonical description.
                fos = dfg.field_of_science
                if fos.description != description or not fos.is_selectable:
                    fos.description = description
                    fos.is_selectable = True
                    fos.save(update_fields=["description", "is_selectable"])
                for attr, value in defaults.items():
                    setattr(dfg, attr, value)
                dfg.save(update_fields=list(defaults))
                stats["FieldOfScience"]["updated"] += 1
                stats["DfgSubject"]["updated"] += 1

        # Project.field_of_science defaults to FieldOfScience.DEFAULT_PK
        # (an NSF fixture row). Make sure it exists and stays selectable so
        # project creation paths relying on the model default keep working;
        # the other NSF rows are never touched.
        default_pk = getattr(FieldOfScience, "DEFAULT_PK", 149)
        default_fos, created = FieldOfScience.objects.get_or_create(
            pk=default_pk,
            defaults={"description": "Other", "is_selectable": True},
        )
        if not created and not default_fos.is_selectable:
            default_fos.is_selectable = True
            default_fos.save(update_fields=["is_selectable"])

    return stats
