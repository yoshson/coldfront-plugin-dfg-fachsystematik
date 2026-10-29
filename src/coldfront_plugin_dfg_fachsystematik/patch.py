"""Glue between this plugin and ColdFront's project forms.

ColdFront (as of 1.1.x and current main) offers no extension point for
modifying the field of science selection, and the core forms select *all*
``FieldOfScience`` rows. The plugin therefore patches both project forms at
application startup:

- ``ProjectCreateView.form_class`` is replaced with a subclass whose
  ``field_of_science`` field is the grouped DFG selector,
- ``ProjectUpdateView.get_form`` is wrapped to apply the same selector to the
  generated update form (only if it actually contains a
  ``field_of_science`` field, i.e. ``PROJECT_UPDATE_FIELDS`` is respected),
  and
- ``ProjectAdmin`` is extended so the Django admin project change form also
  shows ``field_of_science`` with the same selector: ColdFront 1.1.x lists
  the change-form fields in a hardcoded ``fields_change`` tuple that omits
  the field entirely.

The selected subject is saved on the core ``Project.field_of_science``
foreign key; no extra save step or model is involved. If ColdFront's
internals change in an incompatible way, this is the only module that needs
to be adapted.
"""

import logging

logger = logging.getLogger(__name__)


def apply_patches():
    """Use the DFG subject selector in ColdFront's project forms and admin.

    Idempotent: calling it multiple times (e.g. during tests) is safe.
    """
    from coldfront.core.project import admin as project_admin
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

    project_admin_class = project_admin.ProjectAdmin

    # ColdFront 1.1.x hardcodes the fields of the project *change* page in
    # `fields_change` and omits field_of_science, so the value cannot be
    # seen or corrected in the admin. Add it to the tuple (the add page
    # already shows all model fields).
    fields_change = getattr(project_admin_class, "fields_change", None)
    if fields_change is None:
        logger.warning(
            "DFG Fachsystematik plugin: coldfront.core.project.admin."
            "ProjectAdmin has no fields_change attribute; the project admin"
            " change form will not show the field of science. Adapt "
            "patch.py to the ColdFront version in use."
        )
    elif "field_of_science" not in fields_change:
        project_admin_class.fields_change = (*fields_change, "field_of_science")

    # Render the field with the same grouped DFG selector as the front-end
    # forms. formfield_for_foreignkey is Django admin's documented hook for
    # the FK field of the auto-generated ModelForm, so no get_form wrapping
    # is needed. Without select2 being initialized in the admin template the
    # widget degrades to a plain (still grouped) <select>.
    if not getattr(project_admin_class, "_dfg_field_of_science_patched", False):
        original_formfield_for_foreignkey = project_admin_class.formfield_for_foreignkey

        def formfield_for_foreignkey(self, db_field, request, **kwargs):
            if db_field.name == "field_of_science":
                # Bypassing db_field.formfield skips its blank→required
                # translation, so restore it: the FK is null/blank=True and
                # a subject must stay optional in the admin.
                kwargs.setdefault("required", not db_field.blank)
                return DfgFieldOfScienceChoiceField(**kwargs)
            return original_formfield_for_foreignkey(self, db_field, request, **kwargs)

        project_admin_class.formfield_for_foreignkey = formfield_for_foreignkey
        project_admin_class._dfg_field_of_science_patched = True

        logger.info(
            "DFG Fachsystematik plugin: patched project admin to show the "
            "field of science with the DFG subject selector."
        )
