"""Pure parsing helpers for the DFG Fachsystematik CSV.

This module deliberately has no Django imports so that it can be used and
tested standalone, and from data migrations without a full application
registry.
"""

import csv
import os
import re
from dataclasses import dataclass
from importlib.resources import files
from typing import IO

#: The bundled CSV file shipping with the plugin.
BUNDLED_CSV = "Fachsystematik_2024-2028.csv"

#: Hyphenation artifacts carried over from the DFG source (e.g. the subject
#: area "Geowissen-schaften", which is "Geowissenschaften" split across a line
#: break in the original). A hyphen directly followed by a lowercase letter
#: only occurs in these artifacts in the level columns of the source data.
_HYPHENATION_RE = re.compile(r"-(?=[a-zäöüß])")


@dataclass(frozen=True)
class FachsystematikEntry:
    """One row of the Fachsystematik: a subject with its full ancestry."""

    number: str
    subject_en: str
    subject_de: str
    review_board_number: str
    review_board_en: str
    review_board_de: str
    subject_area_number: str
    subject_area_en: str
    subject_area_de: str
    scientific_discipline_number: str
    scientific_discipline_en: str
    scientific_discipline_de: str


def bundled_csv_path() -> files:
    """Return the bundled Fachsystematik CSV as an importlib.resources path."""
    return files("coldfront_plugin_dfg_fachsystematik").joinpath("data", BUNDLED_CSV)


def _clean_name(name: str) -> str:
    """Collapse all whitespace in a name."""
    return " ".join(name.split())


def _repair_hyphenation(name: str) -> str:
    """Remove line-break hyphenation artifacts from a hierarchy-level name.

    Only used for the review board / subject area / scientific discipline
    columns, where a hyphen directly followed by a lowercase letter occurs
    solely in artifacts (subject area 34, "Geowissen-schaften"). Subject
    names contain legitimate lowercase-after-hyphen words (e.g.
    "Literatur-und", "BWL-spezifische") and must not be touched.
    """
    return _HYPHENATION_RE.sub("", name)


def _split_number_and_name(value: str, row_number: str, column: str) -> tuple:
    """Split '111\\nAncient Cultures' into ('111', 'Ancient Cultures')."""
    number, separator, name = value.partition("\n")
    number = number.strip()
    name = _repair_hyphenation(_clean_name(name))
    if not separator or not number or not name:
        raise ValueError(
            f"Row {row_number!r}: column {column!r} does not have the "
            f"expected '<number>\\n<name>' format: {value!r}"
        )
    return number, name


def _get(row: dict, column: str, row_number: str) -> str:
    try:
        return row[column]
    except KeyError as exc:
        raise ValueError(
            f"Row {row_number!r}: missing expected column {column!r}"
        ) from exc


def parse_fachsystematik_csv(source: str | bytes | IO | None = None) -> list:
    """Parse a Fachsystematik CSV into a list of ``FachsystematikEntry``.

    ``source`` may be a filesystem path, a file opened in text mode, or
    ``None`` to use the CSV bundled with the plugin. Files opened by this
    function are closed before returning; files passed in are left open
    for the caller to manage.
    """
    opened = None
    if source is None:
        # Traversable resources must be opened explicitly before csv can
        # read from them.
        opened = source = bundled_csv_path().open("r", newline="", encoding="utf-8")
    elif isinstance(source, (os.PathLike, str, bytes)):
        # Treat paths (str, bytes, os.PathLike) as filesystem paths, not as
        # raw CSV content, to mirror management command ergonomics.
        # Closed manually in the finally block below (SIM115 does not see
        # that, and a with-block would also close caller-owned files).
        opened = source = open(  # noqa: SIM115
            source, newline="", encoding="utf-8"
        )

    try:
        entries = []
        reader = csv.DictReader(source)
        for row in reader:
            number = _get(row, "Subject Number", str(reader.line_num)).strip()
            number_de = _get(row, "Fachnummer", str(reader.line_num)).strip()
            if not number:
                raise ValueError(f"Row {reader.line_num}: empty subject number")
            if number != number_de:
                raise ValueError(
                    f"Row {number!r}: English subject number "
                    f"{number!r} does not match German subject number {number_de!r}"
                )

            rb_num, rb_en = _split_number_and_name(
                _get(row, "Review Board", number), number, "Review Board"
            )
            rb_num_de, rb_de = _split_number_and_name(
                _get(row, "Fachkollegium", number), number, "Fachkollegium"
            )
            sa_num, sa_en = _split_number_and_name(
                _get(row, "Subject Area", number), number, "Subject Area"
            )
            sa_num_de, sa_de = _split_number_and_name(
                _get(row, "Fachgebiet", number), number, "Fachgebiet"
            )
            sd_num, sd_en = _split_number_and_name(
                _get(row, "Scientific Discipline", number),
                number,
                "Scientific Discipline",
            )
            sd_num_de, sd_de = _split_number_and_name(
                _get(row, "Wissenschaftsbereich", number),
                number,
                "Wissenschaftsbereich",
            )
            if not (
                rb_num == rb_num_de and sa_num == sa_num_de and sd_num == sd_num_de
            ):
                raise ValueError(
                    f"Row {number!r}: English and German hierarchy numbers do "
                    f"not match ({rb_num}/{rb_num_de}, {sa_num}/{sa_num_de}, "
                    f"{sd_num}/{sd_num_de})"
                )

            subject_en = _clean_name(_get(row, "Subject", number))
            subject_de = _clean_name(_get(row, "Fach", number))
            if not subject_en or not subject_de:
                raise ValueError(f"Row {number!r}: missing subject name")

            entries.append(
                FachsystematikEntry(
                    number=number,
                    subject_en=subject_en,
                    subject_de=subject_de,
                    review_board_number=rb_num,
                    review_board_en=rb_en,
                    review_board_de=rb_de,
                    subject_area_number=sa_num,
                    subject_area_en=sa_en,
                    subject_area_de=sa_de,
                    scientific_discipline_number=sd_num,
                    scientific_discipline_en=sd_en,
                    scientific_discipline_de=sd_de,
                )
            )

        if not entries:
            raise ValueError("No entries found in Fachsystematik CSV")

        return entries
    finally:
        if opened is not None:
            opened.close()
