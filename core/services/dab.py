"""Integration with the `DadosAbertosBrasil` package.

This module mirrors a subset of the helpers from :mod:`core.services.ibge`
using the high level abstractions provided by the external library.
"""

from __future__ import annotations

from typing import Iterable, List, Optional

from django.db import transaction
from DadosAbertosBrasil import ibge as dab_ibge

from .ibge import _ensure_regiao, _ensure_estado, _ensure_municipio, _normalize_payload
from core.models import Regiao, Estado, Municipio


# Fetch helpers ------------------------------------------------------------

def get_regioes(regiao_id: Optional[int] = None, verify: bool = True):
    """Retrieve regions as JSON objects."""

    localidade = str(regiao_id) if regiao_id else None
    return dab_ibge.localidades(
        nivel="regioes",
        localidade=localidade,
        formato="json",
        verificar_certificado=verify,
    )


def get_estados(
    estado_id: Optional[int] = None,
    regiao_id: Optional[int] = None,
    verify: bool = True,
):
    """Retrieve states as JSON objects."""

    if estado_id:
        return dab_ibge.localidades(
            nivel="estados",
            localidade=str(estado_id),
            formato="json",
            verificar_certificado=verify,
        )
    if regiao_id:
        return dab_ibge.localidades(
            nivel="regioes",
            divisoes="estados",
            localidade=str(regiao_id),
            formato="json",
            verificar_certificado=verify,
        )
    return dab_ibge.localidades(
        nivel="estados", formato="json", verificar_certificado=verify
    )


def get_municipios(
    municipio_id: Optional[int] = None,
    estado_id: Optional[int] = None,
    verify: bool = True,
):
    """Retrieve municipalities as JSON objects."""

    if municipio_id:
        return dab_ibge.localidades(
            nivel="municipios",
            localidade=str(municipio_id),
            formato="json",
            verificar_certificado=verify,
        )
    if estado_id:
        return dab_ibge.localidades(
            nivel="estados",
            divisoes="municipios",
            localidade=str(estado_id),
            formato="json",
            verificar_certificado=verify,
        )
    return dab_ibge.localidades(
        nivel="municipios", formato="json", verificar_certificado=verify
    )


# Sync helpers -------------------------------------------------------------

def sync_regioes(
    regiao_id: Optional[int] = None,
    ids: Optional[Iterable[int]] = None,
    verify: bool = True,
) -> List[Regiao]:
    """Fetch regions from the API and persist them to the database."""

    payload = []
    if ids:
        for _id in ids:
            payload.extend(_normalize_payload(get_regioes(_id, verify=verify)))
    else:
        payload.extend(_normalize_payload(get_regioes(regiao_id, verify=verify)))

    with transaction.atomic():
        regioes = [_ensure_regiao(item) for item in payload]
    return regioes


def sync_estados(
    estado_id: Optional[int] = None,
    regiao_id: Optional[int] = None,
    ids: Optional[Iterable[int]] = None,
    verify: bool = True,
) -> List[Estado]:
    """Fetch states from the API and persist them to the database."""

    payload: List[dict] = []
    if ids:
        for _id in ids:
            payload.extend(
                _normalize_payload(get_estados(_id, None, verify=verify))
            )
    else:
        payload.extend(
            _normalize_payload(get_estados(estado_id, regiao_id, verify=verify))
        )

    with transaction.atomic():
        estados = [_ensure_estado(item) for item in payload]
    return estados


def sync_municipios(
    municipio_id: Optional[int] = None,
    estado_id: Optional[int] = None,
    ids: Optional[Iterable[int]] = None,
    verify: bool = True,
) -> List[Municipio]:
    """Fetch municipalities from the API and persist them to the database."""

    payload: List[dict] = []
    if ids:
        for _id in ids:
            payload.extend(
                _normalize_payload(get_municipios(_id, None, verify=verify))
            )
    else:
        payload.extend(
            _normalize_payload(
                get_municipios(municipio_id, estado_id, verify=verify)
            )
        )

    with transaction.atomic():
        municipios = [_ensure_municipio(item) for item in payload]
    return municipios

