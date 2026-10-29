"""Fixtures for the ColdFront integration tests.

The database is created and migrated by pytest-django (which runs the
plugin's data migration importing the 214 DFG subjects on a fresh database).
A session fixture then rounds it off into a *basic ColdFront instance*:

- ColdFront's status choices (``ProjectStatusChoice`` etc.) are not created
  by migrations but by its ``add_default_project_choices`` command,
- ColdFront's ``import_field_of_science_data`` command deletes and recreates
  the ``FieldOfScience`` table with the NSF rows at their canonical primary
  keys (including the "Other" row behind ``FieldOfScience.DEFAULT_PK``) —
  cascading away the DFG rows created by the plugin's data migration,
- the plugin's ``load_dfg_fachsystematik`` command then re-imports the DFG
  subjects, exactly as the README's "Interplay with
  import_field_of_science_data" section prescribes for real deployments.
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command


@pytest.fixture(scope="session", autouse=True)
def coldfront_test_instance(django_db_setup, django_db_blocker):
    """Set up the basic ColdFront test instance once per test session."""
    with django_db_blocker.unblock():
        call_command("add_default_project_choices")
        call_command("import_field_of_science_data")
        call_command("load_dfg_fachsystematik")


@pytest.fixture
def pi_user(db):
    """A user who may create projects (ColdFront checks userprofile.is_pi)."""
    user = get_user_model().objects.create_user(
        username="test-pi", password="test-password"
    )
    user.userprofile.is_pi = True
    user.userprofile.save()
    return user


@pytest.fixture
def pi_client(client, pi_user):
    """A Django test client logged in as the PI."""
    client.force_login(pi_user)
    return client


@pytest.fixture
def dfg_subject(db):
    """A representative DFG subject, e.g. for project creation POSTs."""
    from coldfront_plugin_dfg_fachsystematik.models import DfgSubject

    return DfgSubject.objects.get(number="111-01")
