"""Form integration: turns ColdFront's field of science selection into a
searchable, grouped DFG Fachsystematik subject selector.

The selection is stored on the core ``Project.field_of_science`` foreign key;
this module only changes *how* the options are presented: a select2 dropdown
whose options are the 214 DFG subjects, grouped by review board
(Fachkollegium), labelled in English and German so both languages are
searchable. ColdFront ships select2 and initializes it on elements with the
``fos-select2`` class, so reusing that class gives us the search box without
extra JavaScript.
"""

from typing import ClassVar

from coldfront.core.field_of_science.models import FieldOfScience
from coldfront.core.project.forms import ProjectCreationForm
from django import forms


def board_group_label(dfg_subject):
    """Optgroup label for a subject's review board (Fachkollegium)."""
    return (
        f"{dfg_subject.board_number} {dfg_subject.board_name_en}"
        f" · {dfg_subject.board_name_de}"
    )


def subject_option_label(field_of_science):
    """Dropdown label for a subject, bilingual so both languages are searchable."""
    dfg_subject = field_of_science.dfg_subject
    return f"{field_of_science.description} · {dfg_subject.name_de}"


def dfg_subject_queryset():
    """All ColdFront fields of science that are DFG subjects, in hierarchy order."""
    return (
        FieldOfScience.objects.filter(dfg_subject__isnull=False)
        .select_related("dfg_subject")
        .order_by("dfg_subject__board_number", "dfg_subject__number")
    )


class DfgFieldOfScienceChoiceField(forms.ModelChoiceField):
    """A ModelChoiceField over FieldOfScience, grouped by review board.

    ChoiceWidget.optgroups renders entries whose label is a list/tuple as
    <optgroup>, so ModelChoiceField's flat iterator is replaced with grouped
    choices below. Validation stays queryset-based and untouched.

    NOTE: the queryset setter of ModelChoiceField forwards the choices to the
    widget, so the choices getter runs once per field instantiation; the
    queryset caches its rows, so repeated access is cheap.
    """

    default_widget_attrs: ClassVar[dict[str, str]] = {
        "class": "fos-select2",
        "data-placeholder": "Select a subject (Fach)",
    }

    def __init__(self, *, queryset=None, **kwargs):
        kwargs.setdefault("label", "Field of Science (DFG Fachsystematik)")
        kwargs.setdefault(
            "help_text",
            "Select the subject (Fach) that best describes this project "
            "according to the DFG classification of scientific disciplines "
            "(Fachsystematik 2024–2028).",
        )
        kwargs.setdefault("empty_label", "")
        if queryset is None:
            queryset = dfg_subject_queryset()
        super().__init__(queryset, **kwargs)
        for attr, value in self.default_widget_attrs.items():
            self.widget.attrs.setdefault(attr, value)

    @property
    def choices(self):
        # Build grouped choices: [(group_label, [(pk, label), ...]), ...].
        grouped = []
        for field_of_science in self.queryset:
            group = board_group_label(field_of_science.dfg_subject)
            if not grouped or grouped[-1][0] != group:
                grouped.append((group, []))
            grouped[-1][1].append(
                (field_of_science.pk, subject_option_label(field_of_science))
            )
        if self.empty_label is not None:
            grouped.insert(0, ("", self.empty_label))
        return grouped

    @choices.setter
    def choices(self, value):
        # Mirror ChoiceField._set_choices for anyone assigning choices
        # manually: forward them to the widget for rendering.
        self.widget.choices = value

    def label_from_instance(self, obj):
        return subject_option_label(obj)


class ProjectCreationFormWithDfgFieldOfScience(ProjectCreationForm):
    """ColdFront's project creation form selecting the DFG subject on the
    core field_of_science foreign key, with a grouped bilingual dropdown."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Replace the flat all-fields dropdown with the grouped DFG selector.
        # The saved value lands on Project.field_of_science natively.
        self.fields["field_of_science"] = DfgFieldOfScienceChoiceField()
