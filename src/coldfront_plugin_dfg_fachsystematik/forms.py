"""Forms for the DFG Fachsystematik plugin (ColdFront 2.x)."""

from typing import ClassVar

from coldfront.lib.forms import ColdFrontModelForm
from coldfront.lib.forms.layout import FieldSet
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import DfgSubject, ProjectSubjectAssignment


def board_group_label(dfg_subject):
    """Optgroup label for a subject's review board (Fachkollegium)."""
    return (
        f"{dfg_subject.board_number} {dfg_subject.board_name_en}"
        f" · {dfg_subject.board_name_de}"
    )


def subject_option_label(dfg_subject):
    """Dropdown label for a subject, bilingual so both languages are searchable."""
    return f"{dfg_subject.number} {dfg_subject.name_en} · {dfg_subject.name_de}"


class DfgSubjectChoiceField(forms.ModelChoiceField):
    """A ModelChoiceField over DfgSubject, grouped by review board.

    ChoiceWidget.optgroups renders entries whose label is a list/tuple as
    <optgroup>, so replacing the flat choices iterator with grouped choices
    is enough. Validation stays queryset-based and untouched.
    """

    def __init__(self, *, queryset=None, **kwargs):
        kwargs.setdefault("label", _("Subject (Fach)"))
        kwargs.setdefault(
            "help_text",
            _("Select the subject (Fach) that best describes this project."),
        )
        kwargs.setdefault("empty_label", "")
        super().__init__(queryset or DfgSubject.objects.all(), **kwargs)

    @property
    def choices(self):
        # Grouped choices: [(group_label, [(pk, label), ...]), ...].
        grouped: list[tuple[str, list[tuple[int, str]]]] = []
        for dfg_subject in self.queryset:
            label = (board_group_label(dfg_subject), [])
            if not grouped or grouped[-1][0] != label[0]:
                grouped.append(label)
            grouped[-1][1].append((dfg_subject.pk, subject_option_label(dfg_subject)))
        return grouped


class ProjectSubjectAssignmentForm(ColdFrontModelForm):
    """Assign a DFG subject to a project.

    The project is not a form field: the edit view sets it from the URL
    before the form is bound, so the form only manages the subject.
    """

    class Meta:
        model = ProjectSubjectAssignment
        fields: ClassVar[tuple[str, ...]] = ("subject", "tags")
        fieldsets = (
            FieldSet("subject", name=_("DFG Fachsystematik")),
            FieldSet("tags", name=_("Tags")),
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["subject"] = DfgSubjectChoiceField()
