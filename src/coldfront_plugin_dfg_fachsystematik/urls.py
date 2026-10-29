"""Plugin URL patterns, mounted under ``/plugins/dfg_fachsystematik/``.

Model views registered via ``register_model_view`` are pulled in with
``get_model_urls``, mirroring how ``coldfront.ras.urls`` wires up core
models. Views registered against ``ras.Project`` are reachable in the
``ras`` namespace (see ``coldfront.lib.registry``).
"""

from coldfront.lib.registry import get_model_urls
from django.urls import include, path

from . import views  # noqa: F401  (importing registers the model views)

urlpatterns = [
    path(
        "subjects/",
        include(
            get_model_urls(
                "coldfront_plugin_dfg_fachsystematik", "dfgsubject", detail=False
            )
        ),
    ),
    path(
        "subjects/<int:pk>/",
        include(get_model_urls("coldfront_plugin_dfg_fachsystematik", "dfgsubject")),
    ),
    path(
        "assignments/",
        include(
            get_model_urls(
                "coldfront_plugin_dfg_fachsystematik",
                "projectsubjectassignment",
                detail=False,
            )
        ),
    ),
    path(
        "assignments/<int:pk>/",
        include(
            get_model_urls(
                "coldfront_plugin_dfg_fachsystematik", "projectsubjectassignment"
            )
        ),
    ),
]
