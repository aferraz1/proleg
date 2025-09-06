from __future__ import annotations

from typing import Iterable, List, Optional

import requests
from django.core.files.base import ContentFile
from DadosAbertosBrasil.uf import UF

from .models import Estado


def _get_image(url: str, verify: bool = True) -> bytes:
    """Download raw image bytes from ``url``.

    Parameters
    ----------
    url: str
        Address of the image resource.
    verify: bool, default=True
        SSL certificate verification flag forwarded to :func:`requests.get`.
    """

    response = requests.get(url, timeout=30, verify=verify)
    response.raise_for_status()
    return response.content


def update_estado_images(
    estado: Estado, tamanho: int = 200, verify: bool = True
) -> Estado:
    """Fetch bandeira and brasão for ``estado`` and store them in the database.

    Parameters
    ----------
    estado:
        Instance of :class:`Estado` to update.
    tamanho: int, default=200
        Desired size in pixels for both images.
    verify: bool, default=True
        Whether to verify SSL certificates when requesting resources.
    """

    uf = UF(estado.sigla, verificar_certificado=verify)
    flag_url = uf.bandeira(tamanho=tamanho)
    coat_url = uf.brasao(tamanho=tamanho)

    bandeira_bytes = _get_image(flag_url, verify=verify)
    brasao_bytes = _get_image(coat_url, verify=verify)

    estado.bandeira.save(
        f"{estado.sigla.lower()}_bandeira.png", ContentFile(bandeira_bytes), save=False
    )
    estado.brasao.save(
        f"{estado.sigla.lower()}_brasao.png", ContentFile(brasao_bytes), save=False
    )
    estado.save(update_fields=["bandeira", "brasao"])
    return estado


def sync_estados_imagens(
    queryset: Optional[Iterable[Estado]] = None,
    siglas: Optional[Iterable[str]] = None,
    tamanho: int = 200,
    verify: bool = True,
) -> List[Estado]:
    """Update bandeira and brasão images for multiple ``Estado`` records."""

    if queryset is None:
        if siglas:
            queryset = Estado.objects.filter(sigla__in=[s.upper() for s in siglas])
        else:
            queryset = Estado.objects.all()

    updated: List[Estado] = []
    for estado in queryset:
        updated.append(update_estado_images(estado, tamanho=tamanho, verify=verify))
    return updated
