"""Navigation menu contributions for the DFG Fachsystematik plugin."""

from coldfront.lib.plugins.navigation import PluginMenuItem
from django.utils.translation import gettext_lazy as _

menu_items = (
    PluginMenuItem(
        link="coldfront_plugin_dfg_fachsystematik:dfgsubject_list",
        link_text=_("DFG Fachsystematik"),
        auth_required=True,
        staff_only=True,
    ),
)
