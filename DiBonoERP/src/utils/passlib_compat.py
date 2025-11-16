"""Compatibility helpers for passlib + bcrypt.

Passlib<1.8 expects the upstream ``bcrypt`` package to expose ``__about__.__version__``.
Recent bcrypt versions (>=4.1) removed that module, which causes passlib to crash
while importing its bcrypt backend.  This helper reinstates the attribute when needed
so we can keep using the latest security patches without pinning older wheels.
"""
from __future__ import annotations

import importlib
from types import SimpleNamespace


def ensure_bcrypt_about() -> None:
    """Ensure the installed ``bcrypt`` module exposes ``__about__.__version__``."""
    bcrypt = importlib.import_module("bcrypt")

    # Newer releases expose ``__version__`` directly on the module but no ``__about__``.
    if getattr(bcrypt, "__about__", None) is None:
        version = getattr(bcrypt, "__version__", "unknown")
        bcrypt.__about__ = SimpleNamespace(__version__=version)


__all__ = ["ensure_bcrypt_about"]
