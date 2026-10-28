"""Management command to (re-)import the DFG Fachsystematik from CSV."""

from pathlib import Path

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

from ... import loaders, parsers


class Command(BaseCommand):
    help = (
        "Import or update the DFG Fachsystematik (2024–2028) from the CSV "
        "bundled with the plugin (or from --path). The import is idempotent "
        "and non-destructive: existing entries are updated in place, entries "
        "absent from the CSV are kept."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            type=Path,
            default=None,
            help=(
                "Path to a Fachsystematik CSV file. Defaults to the "
                "Fachsystematik_2024-2028.csv bundled with the plugin."
            ),
        )

    def handle(self, *args, **options):
        try:
            entries = parsers.parse_fachsystematik_csv(options["path"])
        except (OSError, ValueError) as exc:
            raise CommandError(f"Failed to parse Fachsystematik CSV: {exc}") from exc

        stats = loaders.import_fachsystematik(apps, entries)

        for model_name, counts in stats.items():
            self.stdout.write(
                f"{model_name}: {counts['created']} created, "
                f"{counts['updated']} updated"
            )
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported {len(entries)} subjects (DFG Fachsystematik)."
            )
        )
