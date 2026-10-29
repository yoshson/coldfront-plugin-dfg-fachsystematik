# coldfront-plugin-dfg-fachsystematik

A [ColdFront](https://docs.coldfront.dev/) plugin that lets staff and PIs
assign each project a **subject from the DFG Fachsystematik (2024–2028)** —
the classification of scientific disciplines, subject areas, review boards
and subjects published by the Deutsche Forschungsgemeinschaft (DFG, German
Research Foundation).

> **Branch note:** this branch targets **ColdFront 2.0.x** and integrates
> through ColdFront's plugin API (`coldfront.lib.plugins.PluginConfig`).
> For ColdFront 1.1.x, see the [`main` branch](https://github.com/yoshson/coldfront-plugin-dfg-fachsystematik/tree/main),
> which stores the subjects in ColdFront's legacy `FieldOfScience` table
> instead.

## How it works

ColdFront 2.x has no built-in field-of-science concept, so the plugin owns
the classification data end to end:

- `DfgSubject` — each of the 214 DFG subjects (Fächer), carrying its official
  number (e.g. `213-01`), the English and German subject names, and the
  numbers/names of the review board (Fachkollegium), subject area
  (Fachgebiet) and scientific discipline (Wissenschaftsbereich) above it.
  Sourced from the same bilingual CSV used by the
  [DFG-Fachsystematik-Ontology](https://github.com/tibonto/DFG-Fachsystematik-Ontology)
  project.
- `ProjectSubjectAssignment` — links a `ras.Project` to the subject that best
  describes it (one subject per project).

Both models derive from ColdFront's `ColdFrontModel` base, so they get
change logging, tags and custom-field support for free.

### The hierarchy

```
Scientific Discipline (Wissenschaftsbereich)      e.g.  2 Life Sciences
└── Subject Area (Fachgebiet)                            21 Biology
    └── Review Board (Fachkollegium)                     213 Zoology
        └── Subject (Fach)                               213-01 Systematics and Morphology (Zoology)
```

## Installation

The plugin requires a ColdFront 2.0.x deployment (Python ≥ 3.12,
Django ≥ 5.2). It is not published on PyPI (yet); install it directly from
the [GitHub repository](https://github.com/yoshson/coldfront-plugin-dfg-fachsystematik)
inside your ColdFront environment:

```console
$ uv pip install "coldfront-plugin-dfg-fachsystematik @ git+https://github.com/yoshson/coldfront-plugin-dfg-fachsystematik.git@feat/coldfront-2"
```

Enable it by listing the plugin in the `PLUGINS` environment variable
(comma-separated if you use several):

```console
$ export PLUGINS=coldfront_plugin_dfg_fachsystematik
```

No plugin-specific configuration is required. Then run migrations and load
the bundled Fachsystematik CSV:

```console
$ coldfront migrate
$ coldfront load_dfg_fachsystematik
```

The data load is a separate step on this branch — `migrate` creates the
tables, `load_dfg_fachsystematik` imports the 214 subjects.

## What you get

- **Project detail tab** — a *DFG Fachsystematik* tab on the project detail
  page showing the assigned subject with its full ancestry (review board,
  subject area, scientific discipline), with *Assign/Change/Remove* actions
  for users who may change the project.
- **Project detail panel** — a compact card on the project overview page
  showing the assigned subject.
- **Subject browser** — a bilingual, filterable list of all 214 subjects at
  `/plugins/dfg-fachsystematik/subjects/` (also reachable from the
  navigation menu, staff only). Both the English and the German names are
  searchable at every level of the hierarchy, so a German-speaking PI finds
  "Ur- und Frühgeschichte" as easily as an English-speaking one finds
  "Prehistory". Filters exist for review board, subject area and scientific
  discipline numbers.
- **Django admin** — `DfgSubject` and `ProjectSubjectAssignment` are
  registered for low-level housekeeping.

### Permissions

- Viewing the tab/panel and browsing subjects follows `ras.view_project` /
  login, respectively.
- Assigning, changing and removing a subject requires `ras.change_project`
  (typically staff). The 1.x plugin let PIs choose the subject at project
  creation; ColdFront 2.x has no object-level ownership permission hook yet,
  so assignment is currently staff-only. This will be revisited once
  ColdFront 2.x settles its permission model.

## Refreshing the data

The import is idempotent and non-destructive. To re-import or to load a new
Fachsystematik period (e.g. 2028–2032) from a CSV file:

```console
$ coldfront load_dfg_fachsystematik            # bundled 2024–2028 CSV
$ coldfront load_dfg_fachsystematik --path Fachsystematik_2028-2032.csv
```

Existing subjects are updated in place (matched by DFG number); subjects
absent from the CSV remain in the database, so existing assignments stay
valid.

## Data quirks

The source CSV contains a hyphenation artifact for subject area 34
("Geowissen-schaften"); the importer repairs this to "Geowissenschaften".
Other hyphens in names (e.g. "Hals-Nasen-Ohrenheilkunde") are legitimate and
are preserved.

## Development

```console
$ uv sync --group coldfront2    # also pulls ColdFront 2.0.x from the upstream dev branch
$ uv run pytest
$ uv run ruff check
$ uv run ruff format --check
```

The parser is free of Django imports and covered by unit tests; the Django
integration is intended to be exercised inside a ColdFront 2.0.x test
deployment. To regenerate migrations after model changes, sync with the
`coldfront2` group and run `makemigrations coldfront_plugin_dfg_fachsystematik`
against a ColdFront settings module.
