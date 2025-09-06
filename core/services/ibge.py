"""Utility functions for retrieving locality data from the IBGE API.

This module wraps the endpoints from `https://servicodados.ibge.gov.br/api` that
provide information about Brazilian geographical divisions.  It offers helper
functions to fetch regions, states and municipalities either in bulk or for a
specific identifier.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

import requests
from django.db import transaction

from core.models import Estado, Municipio, Regiao

BASE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades"


def _request(
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    **request_kwargs: Any,
) -> Any:
    """Perform a GET request against the IBGE API and return the JSON payload.

    Parameters
    ----------
    endpoint:
        Path after the base URL identifying which resource to retrieve.
    params:
        Optional query string parameters to send with the request.
    **request_kwargs:
        Additional keyword arguments forwarded to :func:`requests.get`.

    Raises
    ------
    requests.HTTPError
        If the remote API returns a non-success status code.
    """

    url = f"{BASE_URL}/{endpoint.strip('/')}"
    response = requests.get(url, params=params, timeout=30, **request_kwargs)
    response.raise_for_status()
    return response.json()


def get_regioes(
    regiao_id: Optional[int] = None,
    params: Optional[Dict[str, Any]] = None,
    **request_kwargs: Any,
) -> Any:
    """Return all regions or a single region when ``regiao_id`` is provided."""

    endpoint = f"regioes/{regiao_id}" if regiao_id else "regioes"
    params = {
        "orderBy": "nome",
        "view": "nivelado"
    }
    return _request(endpoint, params=params, **request_kwargs)


def get_estados(
    estado_id: Optional[int] = None,
    regiao_id: Optional[int] = None,
    params: Optional[Dict[str, Any]] = None,
    **request_kwargs: Any,
) -> Any:
    """Return all states, a state by ``estado_id`` or states of a ``regiao_id``.

    When both ``estado_id`` and ``regiao_id`` are provided, ``estado_id`` takes
    precedence and a single state is returned.
    """

    if estado_id:
        endpoint = f"estados/{estado_id}"
    elif regiao_id:
        endpoint = f"regioes/{regiao_id}/estados"
    else:
        endpoint = "estados"
    params = {
        "orderBy": "nome",
        "view": "nivelado"
    }
    return _request(endpoint, params=params, **request_kwargs)


def get_municipios(
    municipio_id: Optional[int] = None,
    estado_id: Optional[int] = None,
    params: Optional[Dict[str, Any]] = None,
    **request_kwargs: Any,
) -> Any:
    """Return municipalities.

    Parameters
    ----------
    municipio_id:
        If provided, retrieves a specific municipality.
    estado_id:
        If provided (and ``municipio_id`` is not), retrieves the municipalities
        for the given state.
    """

    if municipio_id:
        endpoint = f"municipios/{municipio_id}"
    elif estado_id:
        endpoint = f"estados/{estado_id}/municipios"
    else:
        endpoint = "municipios"
    params = {
        "orderBy": "nome",
        "view": "nivelado"
    }
    return _request(endpoint, params=params, **request_kwargs)


# -- Database helpers -----------------------------------------------------

def _ensure_regiao(data: Dict[str, Any]) -> Regiao:
    """Create or update a :class:`Regiao` from API payload."""

    return Regiao.objects.update_or_create(
        id=data["id"],
        defaults={"sigla": data.get("sigla", ""), "nome": data.get("nome", "")},
    )[0]


def _ensure_estado(data: Dict[str, Any]) -> Estado:
    """Create or update an :class:`Estado` and its related region."""

    regiao_data = data.get("regiao")
    regiao = _ensure_regiao(regiao_data) if regiao_data else None
    return Estado.objects.update_or_create(
        id=data["id"],
        defaults={
            "sigla": data.get("sigla", ""),
            "nome": data.get("nome", ""),
            "regiao": regiao,
        },
    )[0]


def _ensure_municipio(data: Dict[str, Any]) -> Municipio:
    """Create or update a :class:`Municipio` and ensure its state exists."""

    uf = (
        data.get("microrregiao", {})
        .get("mesorregiao", {})
        .get("UF")
        or data.get("regiao-imediata", {})
        .get("regiao-intermediaria", {})
        .get("UF")
    )
    estado = _ensure_estado(uf) if uf else None
    return Municipio.objects.update_or_create(
        id=data["id"],
        defaults={"nome": data.get("nome", ""), "estado": estado},
    )[0]


def _normalize_payload(item_or_list: Any) -> List[Dict[str, Any]]:
    """Return payload as a list regardless of the API response shape."""

    if isinstance(item_or_list, list):
        return item_or_list
    return [item_or_list]


def sync_regioes(
    regiao_id: Optional[int] = None,
    ids: Optional[Iterable[int]] = None,
    params: Optional[Dict[str, Any]] = None,
    **request_kwargs: Any,
) -> List[Regiao]:
    """Fetch regions from the API and persist them to the database.

    Parameters
    ----------
    regiao_id:
        Retrieve a single region by its IBGE identifier.
    ids:
        Iterable of region identifiers to fetch individually.
    params:
        Optional query-string parameters accepted by the IBGE API.
    """

    payload: List[Dict[str, Any]] = []
    if ids:
        for _id in ids:
            payload.extend(_normalize_payload(get_regioes(_id, params, **request_kwargs)))
    else:
        payload.extend(_normalize_payload(get_regioes(regiao_id, params, **request_kwargs)))

    with transaction.atomic():
        regioes = [_ensure_regiao(item) for item in payload]
    return regioes


def sync_estados(
    estado_id: Optional[int] = None,
    regiao_id: Optional[int] = None,
    ids: Optional[Iterable[int]] = None,
    params: Optional[Dict[str, Any]] = None,
    **request_kwargs: Any,
) -> List[Estado]:
    """Fetch states from the API and persist them to the database."""

    payload: List[Dict[str, Any]] = []
    if ids:
        for _id in ids:
            payload.extend(_normalize_payload(get_estados(_id, None, params, **request_kwargs)))
    else:
        payload.extend(
            _normalize_payload(
                get_estados(estado_id, regiao_id, params, **request_kwargs)
            )
        )

    with transaction.atomic():
        estados = [_ensure_estado(item) for item in payload]
    return estados


def sync_municipios(
    municipio_id: Optional[int] = None,
    estado_id: Optional[int] = None,
    ids: Optional[Iterable[int]] = None,
    params: Optional[Dict[str, Any]] = None,
    **request_kwargs: Any,
) -> List[Municipio]:
    """Fetch municipalities from the API and persist them to the database."""

    payload: List[Dict[str, Any]] = []
    if ids:
        for _id in ids:
            payload.extend(
                _normalize_payload(get_municipios(_id, None, params, **request_kwargs))
            )
    else:
        payload.extend(
            _normalize_payload(
                get_municipios(municipio_id, estado_id, params, **request_kwargs)
            )
        )

    with transaction.atomic():
        municipios = [_ensure_municipio(item) for item in payload]
    return municipios


# Filter helpers ----------------------------------------------------------

def filter_regioes(**filters: Any) -> Iterable[Regiao]:
    """Return regions from the local database applying ``filters``."""

    return Regiao.objects.filter(**filters)


def filter_estados(**filters: Any) -> Iterable[Estado]:
    """Return states from the local database applying ``filters``."""

    return Estado.objects.filter(**filters)


def filter_municipios(**filters: Any) -> Iterable[Municipio]:
    """Return municipalities from the local database applying ``filters``."""

    return Municipio.objects.filter(**filters)

