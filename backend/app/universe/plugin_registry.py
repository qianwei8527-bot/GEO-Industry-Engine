# GEO Universe Plugin Registry
# Discovers, validates, and manages plugin lifecycle.

import os
import yaml
import importlib
from typing import Dict, List, Optional, Any, Type
from functools import lru_cache

from app.universe.plugin import (
    PluginMeta, ViewPlugin, ObservationPlugin, AgentPlugin, RendererPlugin
)

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
_PLUGINS_PATH = os.path.join(_PROJECT_ROOT, "config", "universe", "plugins.yaml")


class PluginRegistry:
    """Central plugin discovery and lifecycle manager."""

    _instance = None

    def __init__(self, config_path=None):
        if config_path is None:
            config_path = _PLUGINS_PATH
        with open(config_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        self.version = raw.get("version", "unknown")
        self.description = raw.get("description", "")

        self._view_defs = raw.get("view_plugins", {})
        self._observation_defs = raw.get("observation_plugins", {})
        self._agent_defs = raw.get("agent_plugins", {})
        self._renderer_defs = raw.get("renderer_plugins", {})

        self._view_instances = {}
        self._observation_instances = {}
        self._agent_instances = {}
        self._renderer_instances = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    def load_all(self):
        for pid, defn in self._view_defs.items():
            if defn.get("enabled", True):
                self._try_load(pid, defn, "view")
        for pid, defn in self._observation_defs.items():
            if defn.get("enabled", True):
                self._try_load(pid, defn, "observation")
        for pid, defn in self._agent_defs.items():
            if defn.get("enabled", True):
                self._try_load(pid, defn, "agent")
        for pid, defn in self._renderer_defs.items():
            if defn.get("enabled", True):
                self._try_load(pid, defn, "renderer")

    def _try_load(self, pid, defn, category):
        class_path = defn.get("class", "")
        if not class_path:
            return
        try:
            module_path, class_name = class_path.rsplit(".", 1)
            mod = importlib.import_module(module_path)
            cls = getattr(mod, class_name)
            instance = cls()
            instance.meta = PluginMeta(
                plugin_id=pid,
                name=getattr(cls, "name", pid),
                version=getattr(cls, "version", "0.1.0"),
                author=getattr(cls, "author", ""),
                description=getattr(cls, "description", ""),
                category=category,
                config_schema=getattr(cls, "config_schema", {}),
                defaults=defn.get("config", {}),
            )
            if category == "view":
                self._view_instances[pid] = instance
            elif category == "observation":
                self._observation_instances[pid] = instance
            elif category == "agent":
                self._agent_instances[pid] = instance
            elif category == "renderer":
                self._renderer_instances[pid] = instance
        except Exception:
            pass

    def list_plugins(self):
        return {
            "view_plugins": {pid: {"enabled": d.get("enabled", True), "class": d.get("class", "")} for pid, d in self._view_defs.items()},
            "observation_plugins": {pid: {"enabled": d.get("enabled", True), "class": d.get("class", "")} for pid, d in self._observation_defs.items()},
            "agent_plugins": {pid: {"enabled": d.get("enabled", True), "class": d.get("class", "")} for pid, d in self._agent_defs.items()},
            "renderer_plugins": {pid: {"enabled": d.get("enabled", True), "class": d.get("class", "")} for pid, d in self._renderer_defs.items()},
        }

    def export_full(self):
        return {
            "version": self.version,
            "description": self.description,
            "plugins": self.list_plugins(),
            "loaded_count": {
                "views": len(self._view_instances),
                "observations": len(self._observation_instances),
                "agents": len(self._agent_instances),
                "renderers": len(self._renderer_instances),
            },
        }


@lru_cache()
def get_plugin_registry():
    return PluginRegistry.get_instance()
