"""Import parsed Fachsystematik entries into the plugin's DfgSubject table.

Unlike the 1.x plugin, there is no interplay with core ColdFront models:
ColdFront 2.x has no ``FieldOfScience``, and the classification is fully
owned by this plugin. Projects reference subjects through the
``ProjectSubjectAssignment`` model.

The loader works with both the global Django app registry (management
command) and the historical registry passed into data migrations, so it
only uses ``apps.get_model(...)`` instead of importing models directly.
"""

from django.db import transaction

APP_LABEL = "coldfront_plugin_dfg_fachsystematik"

_SUBJECT_FIELDS = (
    "name_en",
    "name_de",
    "board_number",
    "board_name_en",
    "board_name_de",
    "area_number",
    "area_name_en",
    "area_name_de",
    "discipline_number",
    "discipline_name_en",
    "discipline_name_de",
)


def subject_defaults(entry):
    """Model fields for a DFG subject entry, keyed by field name."""
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
    """Upsert the given ``FachsystematikEntry`` objects as ``DfgSubject`` rows.

    The import is idempotent and non-destructive: rows are updated in
    place, matched by DFG number; subjects absent from the CSV are kept in
    the database so existing assignments remain valid.

    Returns a dict with ``created``/``updated`` counters.
    """
    DfgSubject = apps.get_model(APP_LABEL, "DfgSubject")

    stats = {"created": 0, "updated": 0}

    with transaction.atomic():
        for entry in entries:
            _obj, created = DfgSubject.objects.update_or_create(
                number=entry.number,
                defaults=subject_defaults(entry),
            )
            stats["created" if created else "updated"] += 1

    return stats
