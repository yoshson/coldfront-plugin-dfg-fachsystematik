"""Views for the DFG Fachsystematik plugin (ColdFront 2.x).

- A browsable, bilingual subject list at ``/plugins/dfg-fachsystematik/``.
- A "DFG Fachsystematik" tab on the project detail view with the assigned
  subject and the assign/remove actions.
- Assign/remove views for ``ProjectSubjectAssignment``.

Views registered against ``ras.Project`` via ``register_model_view`` appear
as tabs on the core project detail page; the URL names live in the ``ras``
namespace (e.g. ``ras:project_dfg_fachsystematik``).
"""

from coldfront.lib.registry import register_model_view
from coldfront.lib.views import ViewTab, generic
from coldfront.ras.models import Project
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from .filtersets import DfgSubjectFilterSet
from .forms import ProjectSubjectAssignmentForm
from .models import DfgSubject, ProjectSubjectAssignment
from .tables import DfgSubjectTable

#
# Subjects
#


@register_model_view(DfgSubject, "list", path="", detail=False)
class DfgSubjectListView(generic.ObjectListView):
    """Bilingual, filterable list of all imported DFG subjects."""

    queryset = DfgSubject.objects.all()
    filterset = DfgSubjectFilterSet
    table = DfgSubjectTable
    # The subjects are importer-managed reference data: no add/import/
    # edit/rename actions on the list view.
    actions = ()


@register_model_view(DfgSubject)
class DfgSubjectView(generic.ObjectView):
    """Subject detail view with its full Fachsystematik ancestry."""

    queryset = DfgSubject.objects.all()
    actions = ()


#
# Project assignment
#


@register_model_view(Project, "dfg_fachsystematik")
class ProjectDfgSubjectTabView(generic.ObjectView):
    """Project detail tab: the subject assigned to this project."""

    queryset = Project.objects.all()
    template_name = "dfg_fachsystematik/project_tab.html"
    actions = ()
    tab = ViewTab(
        label=_("DFG Fachsystematik"),
        permission="ras.view_project",
        weight=90,
    )

    def get_extra_context(self, request, instance):
        return {
            "assignment": (
                ProjectSubjectAssignment.objects.filter(project=instance)
                .select_related("subject")
                .first()
            ),
        }


@register_model_view(ProjectSubjectAssignment, "add", detail=False)
@register_model_view(ProjectSubjectAssignment, "edit")
class ProjectSubjectAssignmentEditView(generic.ObjectEditView):
    """Create or change a project's subject assignment.

    Required permission is ``ras.change_project`` (overriding the default
    assignment-model permission): assigning a subject is a project-level
    change, mirroring the 1.x plugin where the PI chose the subject at
    project creation.
    """

    queryset = ProjectSubjectAssignment.objects.all()
    form = ProjectSubjectAssignmentForm

    def alter_object(self, obj, request, url_args, url_kwargs):
        if not obj.pk:
            project_pk = request.GET.get("project")
            if project_pk:
                obj.project = get_object_or_404(Project, pk=project_pk)
        return obj

    def get_required_permission(self):
        return "ras.change_project"


@register_model_view(ProjectSubjectAssignment, "delete")
class ProjectSubjectAssignmentDeleteView(generic.ObjectDeleteView):
    """Remove a project's subject assignment."""

    queryset = ProjectSubjectAssignment.objects.all()

    def get_required_permission(self):
        return "ras.change_project"
