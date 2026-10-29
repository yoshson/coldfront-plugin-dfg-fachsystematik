"""PI-facing project forms offer and save DFG subjects.

These tests drive ColdFront's real project create/update views with the
Django test client, so they cover the whole patched stack: view → form →
grouped select2 widget → validation → save on the core
``Project.field_of_science`` foreign key.
"""

import pytest
from coldfront.core.field_of_science.models import FieldOfScience
from coldfront.core.project.models import Project, ProjectStatusChoice
from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.fixture
def project(pi_user, dfg_subject):
    """An existing project of the PI, classified with a DFG subject."""
    return Project.objects.create(
        title="Existing project",
        pi=pi_user,
        status=ProjectStatusChoice.objects.get(name="New"),
        field_of_science=dfg_subject.field_of_science,
    )


class TestProjectCreateForm:
    def test_offers_grouped_dfg_subjects(self, pi_client):
        response = pi_client.get(reverse("project-create"))
        assert response.status_code == 200
        html = response.content.decode()

        # The select2 widget class is what ColdFront's templates initialize.
        assert "fos-select2" in html
        # Options are grouped by review board (Fachkollegium) ...
        assert "<optgroup" in html
        assert "111 Ancient Cultures · Alte Kulturen" in html
        # ... and labelled bilingually, so both languages are searchable.
        assert (
            "111-01 Prehistory and World Archaeology "
            "· Ur- und Frühgeschichte (weltweit)" in html
        )

    def test_offers_only_dfg_subjects(self, pi_client):
        """Non-DFG fields of science (e.g. ColdFront's NSF rows) are not
        offered, even when selectable."""
        FieldOfScience.objects.create(
            description="Some legacy NSF field", is_selectable=True
        )
        response = pi_client.get(reverse("project-create"))
        html = response.content.decode()

        assert "Some legacy NSF field" not in html
        # The default row (FieldOfScience.DEFAULT_PK) is selectable but is
        # not a DFG subject, so it must not appear either.
        assert f">{FieldOfScience.DEFAULT_PK}" not in html

    def test_create_project_saves_dfg_subject(self, pi_client, pi_user, dfg_subject):
        response = pi_client.post(
            reverse("project-create"),
            data={
                "title": "DFG classified project",
                "description": "Created through the real view.",
                "field_of_science": dfg_subject.field_of_science.pk,
            },
        )
        assert response.status_code == 302

        project = Project.objects.get(title="DFG classified project")
        assert project.pi == pi_user
        assert project.field_of_science == dfg_subject.field_of_science
        # ColdFront adds the PI as an active manager on creation.
        assert project.projectuser_set.filter(
            user=pi_user, role__name="Manager", status__name="Active"
        ).exists()

    def test_create_project_rejects_non_dfg_subject(self, pi_client):
        """Only DFG subjects pass validation; other FieldOfScience rows
        (here the DEFAULT_PK row) are rejected."""
        response = pi_client.post(
            reverse("project-create"),
            data={
                "title": "Must not be created",
                "description": "",
                "field_of_science": FieldOfScience.DEFAULT_PK,
            },
        )
        assert response.status_code == 200  # the form is re-rendered
        assert not Project.objects.filter(title="Must not be created").exists()


class TestProjectUpdateForm:
    def test_shows_current_subject_selected(self, pi_client, project):
        response = pi_client.get(reverse("project-update", args=[project.pk]))
        assert response.status_code == 200
        html = response.content.decode()

        assert "fos-select2" in html
        assert f'value="{project.field_of_science.pk}" selected' in html

    def test_update_changes_subject(self, pi_client, project):
        new_subject = (
            FieldOfScience.objects.filter(dfg_subject__isnull=False)
            .exclude(pk=project.field_of_science.pk)
            .first()
        )
        response = pi_client.post(
            reverse("project-update", args=[project.pk]),
            data={
                "title": project.title,
                "description": "Updated through the real view.",
                "field_of_science": new_subject.pk,
            },
        )
        assert response.status_code == 302

        project.refresh_from_db()
        assert project.field_of_science == new_subject

    def test_update_rejects_non_dfg_subject(self, pi_client, project):
        response = pi_client.post(
            reverse("project-update", args=[project.pk]),
            data={
                "title": project.title,
                "description": "",
                "field_of_science": FieldOfScience.DEFAULT_PK,
            },
        )
        assert response.status_code == 200

        project.refresh_from_db()
        assert project.field_of_science.dfg_subject.number == "111-01"
