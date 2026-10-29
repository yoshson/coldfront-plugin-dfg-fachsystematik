"""ColdFront plugin for the DFG Fachsystematik (2024–2028).

This branch targets ColdFront 2.0.x and integrates through ColdFront's
plugin API (``coldfront.lib.plugins.PluginConfig``) instead of the
monkeypatching used on the 1.1.x line.
"""

from .apps import DfgFachsystematikConfig

__all__ = ("DfgFachsystematikConfig",)

# ColdFront's plugin loader expects a module-level ``config`` attribute
# pointing at the PluginConfig subclass (see coldfront.config.plugins).
config = DfgFachsystematikConfig
