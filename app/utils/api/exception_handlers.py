"""
Traduce al español mensajes de error genéricos de Django/DRF en respuestas JSON.
"""

from __future__ import annotations

import re
from typing import Any

from rest_framework.views import exception_handler

# Django: django.shortcuts.get_object_or_404 — «No %(verbose_name)s matches the given query.»
_NO_QUERY_MATCH = re.compile(
    r"^No (?P<verbose>.+?) matches the given query\.$",
    re.IGNORECASE,
)

# verbose_name por defecto o explícito (normalizado en minúsculas) → mensaje en español
_NO_MATCH_ES: dict[str, str] = {
    "image": "No existe ninguna imagen que coincida con la consulta indicada.",
    "user": "No existe ningún usuario que coincida con la consulta indicada.",
    "tag": "No existe ninguna etiqueta que coincida con la consulta indicada.",
    "relacion imagen-etiqueta": (
        "No existe ninguna relación imagen-etiqueta que coincida con la consulta indicada."
    ),
    "regla de recompensa": (
        "No existe ninguna regla de recompensa que coincida con la consulta indicada."
    ),
    "retiro de recompensas": (
        "No existe ningún retiro de recompensas que coincida con la consulta indicada."
    ),
}

_GENERIC_NOT_FOUND_EN = frozenset(
    {
        "Not found.",
        "Not Found",
    }
)


def _normalize_verbose_key(verbose: str) -> str:
    return re.sub(r"\s+", " ", verbose.strip()).lower()


def _translate_not_found_detail(text: str) -> str:
    s = str(text).strip()
    if s in _GENERIC_NOT_FOUND_EN:
        return "No se encontró el recurso solicitado."
    m = _NO_QUERY_MATCH.match(s)
    if not m:
        return text
    key = _normalize_verbose_key(m.group("verbose"))
    return _NO_MATCH_ES.get(
        key,
        "No hay ningún resultado que coincida con la consulta indicada.",
    )


def _translate_data(data: Any) -> Any:
    if data is None:
        return None
    if isinstance(data, (list, tuple)):
        return type(data)(_translate_data(x) for x in data)
    if isinstance(data, dict):
        out = {}
        for k, v in data.items():
            if k == "detail":
                out[k] = _translate_data(v)
            else:
                out[k] = v
        return out
    # ErrorDetail y str
    return _translate_not_found_detail(data)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None and getattr(response, "data", None) is not None:
        response.data = _translate_data(response.data)
    return response
