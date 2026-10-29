"""Template extension: DFG subject panel on the project detail page."""

import contextlib

from coldfront.lib.plugins import PluginTemplateExtension

from .models import ProjectSubjectAssignment


class ProjectDfgSubjectPanel(PluginTemplateExtension):
    """Show the project's assigned DFG subject on its detail page."""

    models = ("ras.Project",)

    def left_page(self):
        assignment = None
        with contextlib.suppress(ProjectSubjectAssignment.DoesNotExist):
            assignment = self.context["object"].dfg_subject_assignment
        return self.render(
            "dfg_fachsystematik/panel_project.html",
            {"assignment": assignment},
        )


template_extensions = (ProjectDfgSubjectPanel,)
