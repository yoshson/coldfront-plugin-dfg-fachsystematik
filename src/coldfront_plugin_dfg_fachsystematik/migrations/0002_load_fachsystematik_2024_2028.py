"""Load the DFG Fachsystematik (2024–2028) bundled with the plugin.

Creates the 214 core FieldOfScience rows for the DFG subjects (Fächer) plus
the plugin's DfgSubject metadata side table.
"""

from django.db import migrations

from coldfront_plugin_dfg_fachsystematik import loaders, parsers


def import_fachsystematik(apps, schema_editor):
    entries = parsers.parse_fachsystematik_csv()
    loaders.import_fachsystematik(apps, entries)


def unimport_fachsystematik(apps, schema_editor):
    # Keep the data on rollback; the schema migration removes the side table
    # anyway, and the core FieldOfScience rows are harmless without it.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("dfg_fachsystematik", "0001_initial"),
        ("field_of_science", "__first__"),
    ]

    operations = [
        migrations.RunPython(import_fachsystematik, unimport_fachsystematik),
    ]
