# coldfront-plugin-dfg-fachsystematik

A [ColdFront](https://coldfront.readthedocs.io/) plugin that lets PIs select a
**field of science for their project according to the DFG
Fachsystematik (2024–2028)** — the classification of scientific disciplines,
subject areas, review boards and subjects published by the Deutsche
Forschungsgemeinschaft (DFG, German Research Foundation).

## How it works

The plugin stores the DFG classification **inside ColdFront's native field
of science data**:

- Each of the 214 DFG subjects (Fächer) is imported as a selectable
  `FieldOfScience` row whose description is the official number plus the
  English name, e.g. `111-01 Prehistory and World Archaeology`.
- The subject chosen at project creation is saved on the project's **core
  `Project.field_of_science` foreign key** — no separate plugin model on the
  project. The subject therefore appears everywhere ColdFront uses the field
  of science: the project detail page, the project update form, project
  search, FOS-based reports and the REST API.
- The plugin's only model, `DfgSubject`, is a side table mapping each such
  row to its DFG metadata: the German subject name and the numbers/names of
  the review board (Fachkollegium), subject area (Fachgebiet) and scientific
  discipline (Wissenschaftsbereich). This keeps the hierarchy queryable
  (e.g. "all projects in subject area 34 Geosciences") and powers the
  selection widget.

### The hierarchy

```
Scientific Discipline (Wissenschaftsbereich)      e.g.  2 Life Sciences
└── Subject Area (Fachgebiet)                            21 Biology
    └── Review Board (Fachkollegium)                     213 Zoology
        └── Subject (Fach)                               213-01 Systematics and Morphology (Zoology)
```

### Easing the selection in the frontend

ColdFront's built-in field of science dropdown is a flat list of all
`FieldOfScience` rows. The plugin replaces the selection field in the
project creation and update forms with a **searchable select2 dropdown whose
options are the 214 DFG subjects, grouped by review board (Fachkollegium)**
via `<optgroup>` headers:

```
111 Ancient Cultures · Alte Kulturen
    111-01 — Prehistory and World Archaeology · Ur- und Frühgeschichte (weltweit)
    111-02 — Greek and Latin Philology · Griechische und Lateinische Philologie
    …
112 History · Geschichtswissenschaften
    …
```

Both the English and the German subject names are searchable, so a
German-speaking PI finds "Ur- und Frühgeschichte" as easily as an
English-speaking one finds "Prehistory". No custom JavaScript is needed:
ColdFront already ships select2 and applies it to the widget class reused
here.

The data ships with the plugin
(`src/coldfront_plugin_dfg_fachsystematik/data/Fachsystematik_2024-2028.csv`)
and is the same bilingual CSV used by the
[DFG-Fachsystematik-Ontology](https://github.com/tibonto/DFG-Fachsystematik-Ontology)
project.

## Installation

The plugin requires a working ColdFront deployment (tested against
ColdFront 1.1.x). It is not published on PyPI (yet); install it directly
from the
[GitHub repository](https://github.com/yoshson/coldfront-plugin-dfg-fachsystematik)
inside your ColdFront environment:

```console
$ uv pip install git+https://github.com/yoshson/coldfront-plugin-dfg-fachsystematik.git
```

Enable the plugin by creating `coldfront/config/plugins/dfg_fachsystematik.py`
in your ColdFront installation:

```python
from coldfront.config.base import INSTALLED_APPS

INSTALLED_APPS += [
    'coldfront_plugin_dfg_fachsystematik',
]
```

and register it in `coldfront/config/settings.py`:

```python
plugin_configs['PLUGIN_DFG_FACHSYSTEMATIK'] = 'plugins/dfg_fachsystematik.py'
```

Then set `PLUGIN_DFG_FACHSYSTEMATIK=True` in your environment (or local
settings) and run migrations:

```console
$ coldfront migrate
```

The initial migration automatically imports the Fachsystematik into the
`FieldOfScience` table. The plugin hooks into the project forms at
application startup — no further wiring is required.

## Refreshing the data

The import is idempotent and non-destructive. To re-import or to load a new
Fachsystematik period (e.g. 2028–2032) from a CSV file:

```console
$ coldfront load_dfg_fachsystematik            # bundled 2024–2028 CSV
$ coldfront load_dfg_fachsystematik --path Fachsystematik_2028-2032.csv
```

Existing subjects are updated in place (matched by DFG number); subjects
absent from the CSV remain in the database. Note that the importer manages
the `description` of the DFG `FieldOfScience` rows — manual edits to those
descriptions in the admin are reverted on the next import.

## Settings

| Setting | Default | Description |
| --- | --- | --- |
| `DFG_FACHSYSTEMATIK_PATCH_PROJECT_FORM` | `True` | Automatically replace the field of science selection in the project create/update forms with the grouped DFG selector. Set to `False` if you want to wire the forms up yourself (use `coldfront_plugin_dfg_fachsystematik.forms.DfgFieldOfScienceChoiceField`) or use the plugin purely as a data importer. |

## Notes on the built-in field of science data

- The prepopulated **NSF `FieldOfScience` rows are left untouched**, and
  existing projects keep their values. Only the create/update forms are
  narrowed to DFG subjects; `is_selectable` alone does not filter the core
  forms.
- When a project with a legacy NSF value is **edited**, the update form
  offers only DFG subjects, so saving requires choosing a DFG subject —
  a natural way to reclassify legacy projects over time.
- ColdFront's FOS-based reports and searches operate on the
  `description`, i.e. on the 214 DFG subjects (leaf level). Aggregations by
  Fachgebiet/Fachkollegium are possible by joining through the plugin's
  `DfgSubject` side table.

### Interplay with `import_field_of_science_data`

ColdFront's own `import_field_of_science_data` command **deletes and
recreates all `FieldOfScience` rows**. On a fresh setup where that command is
run after `migrate`, the DFG rows created by this plugin's data migration are
wiped — simply re-run `load_dfg_fachsystematik` afterwards to restore them
(the plugin's side table cleans itself up via cascade and is recreated with
the data).

⚠️ Do **not** re-run `import_field_of_science_data` on a database that has
projects: `Project.field_of_science` is `on_delete=CASCADE`, so wiping the
`FieldOfScience` table would delete the projects with it. This is core
ColdFront behavior and applies with or without this plugin; it is mentioned
here because DFG subjects live in the same table.

## Django admin

The plugin adds a *DFG subjects (Fächer)* admin section listing all imported
subjects with their metadata and a link to the underlying `FieldOfScience`
row, filterable by scientific discipline and subject area. ColdFront's own
`FieldOfScience` admin remains untouched.

## How the form integration works

ColdFront currently has no extension point for modifying form fields, and
its forms select *all* `FieldOfScience` rows. At application startup
(`AppConfig.ready()`), the plugin therefore:

1. replaces `ProjectCreateView.form_class` with
   `ProjectCreationFormWithDfgFieldOfScience`, whose `field_of_science`
   field is the grouped DFG selector, and
2. wraps `ProjectUpdateView.get_form` to apply the same selector to the
   generated update form (only if it contains a `field_of_science` field,
   so a customized `PROJECT_UPDATE_FIELDS` is respected).

The selection is saved by ColdFront's own ModelForm machinery on the
project's native `field_of_science` foreign key — there is no extra save
step, and the `project_new` signal sees the final value. All patching lives
in `coldfront_plugin_dfg_fachsystematik/patch.py` and is the only module that
needs adapting if ColdFront's internals change.

## Data quirks

The source CSV contains a hyphenation artifact for subject area 34
("Geowissen-schaften"); the importer repairs this to "Geowissenschaften".
Other hyphens in names (e.g. "Hals-Nasen-Ohrenheilkunde") are legitimate and
are preserved.

## Development

```console
$ uv sync
$ uv run pytest
$ uv run ruff check
$ uv run ruff format --check
```

The parser is free of Django imports and covered by unit tests; the Django
integration is intended to be exercised inside a ColdFront test deployment.
