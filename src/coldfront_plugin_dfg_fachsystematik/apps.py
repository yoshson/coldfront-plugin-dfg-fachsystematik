"""Application configuration for the DFG Fachsystematik plugin."""

import logging

from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


class DfgFachsystematikConfig(AppConfig):
    """Configure the plugin and attach it to ColdFront's project forms."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "coldfront_plugin_dfg_fachsystematik"
    label = "dfg_fachsystematik"
    verbose_name = "DFG Fachsystematik"

    def ready(self):
        from django.conf import settings

        # The automatic integration can be disabled, e.g. to wire the form up
        # manually or to use the plugin purely as a data source.
        if not getattr(settings, "DFG_FACHSYSTEMATIK_PATCH_PROJECT_FORM", True):
            logger.info(
                "DFG Fachsystematik plugin: ColdFront integration (project "
                "forms and admin) disabled via "
                "DFG_FACHSYSTEMATIK_PATCH_PROJECT_FORM."
            )
            return

        try:
            from .patch import apply_patches
        except ImportError as exc:  # pragma: no cover - defensive
            raise ImproperlyConfigured(
                "coldfront_plugin_dfg_fachsystematik requires ColdFront to be "
                "installed and is meant to be used inside a ColdFront "
                "deployment. If you do not want the project creation form to "
                "be patched, set DFG_FACHSYSTEMATIK_PATCH_PROJECT_FORM = False "
                "in your ColdFront settings."
            ) from exc

        apply_patches()
