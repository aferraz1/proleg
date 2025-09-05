"""Utility functions for retrieving locality data from the IBGE API.

This module wraps the endpoints from `https://servicodados.ibge.gov.br/api` that
provide information about Brazilian geographical divisions.  It offers helper
functions to fetch regions, states and municipalities either in bulk or for a
specific identifier.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import requests

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
    return _request(endpoint, params=params, **request_kwargs)

