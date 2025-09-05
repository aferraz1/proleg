from django.contrib import admin

from .models import (
    Cor,
    Endereco,
    Estado,
    Municipio,
    Regiao,
    Sexo,
    Telefone,
    TipoEndereco,
    TipoTelefone,
)

admin.site.register([
    Cor,
    Regiao,
    Estado,
    Municipio,
    Sexo,
    TipoTelefone,
    TipoEndereco,
    Endereco,
    Telefone,
])
