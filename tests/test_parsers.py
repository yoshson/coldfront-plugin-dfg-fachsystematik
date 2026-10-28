"""Tests for the pure CSV parser (no Django required)."""

import importlib.resources
import pathlib

import pytest

from coldfront_plugin_dfg_fachsystematik import parsers


def test_bundled_csv_loads():
    entries = parsers.parse_fachsystematik_csv()
    # DFG Fachsystematik 2024-2028: 214 subjects across 49 review boards,
    # 14 subject areas and 4 scientific disciplines.
    assert len(entries) == 214
    assert len({e.review_board_number for e in entries}) == 49
    assert len({e.subject_area_number for e in entries}) == 14
    assert len({e.scientific_discipline_number for e in entries}) == 4


def test_subject_numbers_unique():
    entries = parsers.parse_fachsystematik_csv()
    numbers = [e.number for e in entries]
    assert len(numbers) == len(set(numbers))


def test_known_values():
    entries = {e.number: e for e in parsers.parse_fachsystematik_csv()}

    entry = entries["111-01"]
    assert entry.subject_en == "Prehistory and World Archaeology"
    assert entry.subject_de == "Ur- und Frühgeschichte (weltweit)"
    assert entry.review_board_number == "111"
    assert entry.review_board_en == "Ancient Cultures"
    assert entry.subject_area_number == "11"
    assert entry.subject_area_en == "Humanities"
    assert entry.scientific_discipline_number == "1"
    assert entry.scientific_discipline_en == "Humanities and Social Sciences"
    assert entry.scientific_discipline_de == "Geistes- und Sozialwissenschaften"


def test_whitespace_is_normalized():
    # The source contains numbers like "112 " and "1 " with trailing spaces.
    entries = {e.number: e for e in parsers.parse_fachsystematik_csv()}
    assert "112-01" in entries
    assert entries["112-01"].review_board_number == "112"
    assert entries["112-01"].review_board_en == "History"


def test_hyphenation_artifact_is_repaired():
    # Subject area 34 is "Geowissen-schaften" in the source (a line-break
    # hyphenation artifact) and must be imported as "Geowissenschaften".
    entries = parsers.parse_fachsystematik_csv()
    area_34 = {e.subject_area_number: e for e in entries}["34"]
    assert area_34.subject_area_de == "Geowissenschaften"


def test_german_subject_hyphens_are_preserved():
    # Hyphens in subject names are legitimate and must not be touched, even
    # when followed by a lowercase letter.
    entries = {e.number: e for e in parsers.parse_fachsystematik_csv()}
    assert (
        entries["115-02"].subject_de
        == "Germanistische Literatur-und Kulturwissenschaften (Neuere deutsche Literatur)"
    )
    assert (
        entries["124-05"].subject_de
        == "Operations Management und BWL-spezifische Wirtschaftsinformatik"
    )
    assert (
        entries["222-29"].subject_de
        == "Hals-Nasen-Ohrenheilkunde, Phoniatrie und Audiologie"
    )
    assert (
        entries["312-01"].subject_en
        == "Solid State and Surface Chemistry, Material Synthesis"
    )


def test_parse_from_explicit_path():
    data = importlib.resources.files("coldfront_plugin_dfg_fachsystematik")
    csv_path = data.joinpath("data", parsers.BUNDLED_CSV)
    # Path-like objects (as used by the management command) and strings both work.
    assert len(parsers.parse_fachsystematik_csv(csv_path)) == 214
    assert len(parsers.parse_fachsystematik_csv(str(csv_path))) == 214


def test_empty_csv_raises(tmp_path: pathlib.Path):
    empty = tmp_path / "empty.csv"
    empty.write_text(
        "Subject Number,Subject,Review Board,Subject Area,Scientific Discipline,"
        "Fachnummer,Fach,Fachkollegium,Fachgebiet,Wissenschaftsbereich\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="No entries"):
        parsers.parse_fachsystematik_csv(str(empty))


def test_bad_row_raises(tmp_path: pathlib.Path):
    bad = tmp_path / "bad.csv"
    bad.write_text(
        "Subject Number,Subject,Review Board,Subject Area,Scientific Discipline,"
        "Fachnummer,Fach,Fachkollegium,Fachgebiet,Wissenschaftsbereich\n"
        "111-01,Prehistory," + ",".join(["garbage"] * 8) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        parsers.parse_fachsystematik_csv(str(bad))


def test_mismatched_numbers_raise(tmp_path: pathlib.Path):
    bad = tmp_path / "mismatch.csv"
    bad.write_text(
        "Subject Number,Subject,Review Board,Subject Area,Scientific Discipline,"
        "Fachnummer,Fach,Fachkollegium,Fachgebiet,Wissenschaftsbereich\n"
        '111-01,Prehistory,"111\nAncient Cultures","11\nHumanities",'
        '"1\nHumanities and Social Sciences",'
        '111-02,Ur- und Frühgeschichte,"111\nAlte Kulturen",'
        '"11\nGeisteswissenschaften","1\nGeistes- und Sozialwissenschaften"\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="subject number"):
        parsers.parse_fachsystematik_csv(str(bad))


def test_bundled_csv_ships_in_package():
    """Ensure the data file is not forgotten when packaging (e.g. sdist/wheel)."""
    path = parsers.bundled_csv_path()
    assert path.is_file(), f"missing bundled CSV: {path}"
