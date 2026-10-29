"""Application configuration for the DFG Fachsystematik plugin (ColdFront 2.x)."""

from coldfront.lib.plugins import PluginConfig


class DfgFachsystematikConfig(PluginConfig):
    """Plugin config: subjects browser, project tab, and assignment model.

    ``PluginConfig.ready()`` registers the plugin models with ColdFront's
    model registry (change logging, tags, custom fields) and loads the
    optional resources ``navigation.menu_items`` and
    ``template_content.template_extensions``; no further wiring is needed.
    """

    name = "coldfront_plugin_dfg_fachsystematik"
    verbose_name = "DFG Fachsystematik"
    description = (
        "Classify projects with the DFG Fachsystematik 2024–2028 "
        "(bilingual subject browser and per-project assignment)."
    )
    version = "0.2.0"
    author = "York Schickl"
    author_email = "york.schickl@uni-konstanz.de"

    # The 2.0.x core API is still moving; declare the supported floor.
    min_version = "2.0.0"

    # Mounted under /plugins/dfg-fachsystematik/. Note: the app label must
    # stay the default (the module's last path component) — ColdFront's
    # plugin URL mounting resolves app configs by module name.
    base_url = "dfg-fachsystematik"

    default_auto_field = "django.db.models.BigAutoField"
