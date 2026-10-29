"""The plugin boots inside a real ColdFront 1.1.x instance.

These tests run against a full ColdFront settings module (see
``settings.py``), so a passing ``django_db`` fixture already proves the
central integration step: the plugin's data migration imports the DFG
Fachsystematik into ColdFront's ``FieldOfScience`` table on a fresh
database, and ``AppConfig.ready()`` patches ColdFront's project forms and
admin without breaking startup.
"""

import pytest
from coldfront.core.field_of_science.models import FieldOfScience
from coldfront.core.project import views as project_views
from coldfront.core.project.admin import ProjectAdmin
from django.apps import apps
from django.contrib import admin as django_admin
from django.test import override_settings

from coldfront_plugin_dfg_fachsystematik.admin import DfgFieldOfScienceAdmin
from coldfront_plugin_dfg_fachsystematik.forms import (
    ProjectCreationFormWithDfgFieldOfScience,
)
from coldfront_plugin_dfg_fachsystematik.models import DfgSubject

pytestmark = pytest.mark.django_db


def test_project_create_view_is_patched():
    """The create view's form class is the DFG subject selector form."""
    assert (
        project_views.ProjectCreateView.form_class
        is ProjectCreationFormWithDfgFieldOfScience
    )


def test_project_admin_shows_field_of_science():
    """ColdFront 1.1.x omits field_of_science from fields_change; the
    plugin appends it so the admin change form shows the subject."""
    assert "field_of_science" in ProjectAdmin.fields_change


def test_field_of_science_admin_is_dfg_aware():
    assert isinstance(
        django_admin.site._registry[FieldOfScience], DfgFieldOfScienceAdmin
    )


def test_data_migration_imported_all_subjects():
    """A fresh migrate (run by pytest-django) imported all 214 subjects."""
    assert DfgSubject.objects.count() == 214
    assert FieldOfScience.objects.filter(dfg_subject__isnull=False).count() == 214


def test_canonical_descriptions():
    subject = DfgSubject.objects.get(number="111-01")
    fos = subject.field_of_science
    assert fos.description == "111-01 Prehistory and World Archaeology"
    assert fos.is_selectable


def test_default_field_of_science_row_is_kept_selectable():
    """Project.field_of_science defaults to FieldOfScience.DEFAULT_PK; the
    importer keeps that row in place and selectable."""
    default_fos = FieldOfScience.objects.get(pk=FieldOfScience.DEFAULT_PK)
    assert default_fos.is_selectable
    assert not hasattr(default_fos, "dfg_subject")


def test_patch_setting_disables_integration():
    """DFG_FACHSYSTEMATIK_PATCH_PROJECT_FORM=False leaves the views alone."""
    config = apps.get_app_config("dfg_fachsystematik")
    create_view = project_views.ProjectCreateView
    original_form_class = create_view.form_class

    from coldfront.core.project.forms import ProjectCreationForm

    create_view.form_class = ProjectCreationForm
    try:
        with override_settings(DFG_FACHSYSTEMATIK_PATCH_PROJECT_FORM=False):
            config.ready()
        assert create_view.form_class is ProjectCreationForm
    finally:
        create_view.form_class = original_form_class
        # apply_patches is idempotent: ready() restores the patched view.
        config.ready()

    assert create_view.form_class is ProjectCreationFormWithDfgFieldOfScience
