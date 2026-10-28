"""Glue between this plugin and ColdFront's project forms.

ColdFront (as of 1.1.x and current main) offers no extension point for
modifying the field of science selection, and the core forms select *all*
``FieldOfScience`` rows. The plugin therefore patches both project forms at
application startup:

- ``ProjectCreateView.form_class`` is replaced with a subclass whose
  ``field_of_science`` field is the grouped DFG selector, and
- ``ProjectUpdateView.get_form`` is wrapped to apply the same selector to the
  generated update form (only if it actually contains a
  ``field_of_science`` field, i.e. ``PROJECT_UPDATE_FIELDS`` is respected).

The selected subject is saved on the core ``Project.field_of_science``
foreign key; no extra save step or model is involved. If ColdFront's
internals change in an incompatible way, this is the only module that needs
to be adapted.
"""

import logging

logger = logging.getLogger(__name__)


def apply_patches():
    """Use the DFG subject selector in ColdFront's project forms.

    Idempotent: calling it multiple times (e.g. during tests) is safe.
    """
    from coldfront.core.project import views as project_views

    from .forms import (
        DfgFieldOfScienceChoiceField,
        ProjectCreationFormWithDfgFieldOfScience,
    )

    create_view = project_views.ProjectCreateView

    # The reference to the form class lives on the view class; swapping the
    # module attribute in coldfront.core.project.forms would not be enough.
    if not issubclass(create_view.form_class, ProjectCreationFormWithDfgFieldOfScience):
        create_view.form_class = ProjectCreationFormWithDfgFieldOfScience

        update_view = project_views.ProjectUpdateView
        original_get_form = update_view.get_form

        def get_form(self, form_class=None):
            form = original_get_form(self, form_class)
            if "field_of_science" in form.fields:
                # Replacing the field keeps the instance value: ModelForm
                # populates form.initial from the instance, and the field
                # validates against the same queryset.
                form.fields["field_of_science"] = DfgFieldOfScienceChoiceField()
            return form

        update_view.get_form = get_form

        logger.info(
            "DFG Fachsystematik plugin: patched project create/update forms "
            "to select DFG subjects on the field_of_science foreign key."
        )
