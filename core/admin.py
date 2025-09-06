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
from .services import dab
from . import utils


@admin.register(Regiao)
class RegiaoAdmin(admin.ModelAdmin):
    list_display = ("id", "sigla", "nome")
    search_fields = ("nome", "sigla")
    actions = ["sincronizar_regioes"]

    def sincronizar_regioes(self, request, queryset):
        dab.sync_regioes(verify=False)
        self.message_user(request, "Regiões sincronizadas com DadosAbertosBrasil.")


@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ("id", "sigla", "nome", "regiao")
    search_fields = ("nome", "sigla")
    list_filter = ("regiao",)
    actions = ["sincronizar_estados", "atualizar_imagens"]

    def sincronizar_estados(self, request, queryset):
        dab.sync_estados(verify=False)
        self.message_user(request, "Estados sincronizados com DadosAbertosBrasil.")

    def atualizar_imagens(self, request, queryset):
        atualizados = utils.sync_estados_imagens(queryset=queryset, verify=False)
        self.message_user(
            request,
            f"{len(atualizados)} estados atualizados com bandeiras e brasões.",
        )


@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "estado")
    search_fields = ("nome",)
    list_filter = ("estado",)
    actions = ["sincronizar_municipios"]

    def sincronizar_municipios(self, request, queryset):
        dab.sync_municipios(verify=False)
        self.message_user(request, "Municípios sincronizados com DadosAbertosBrasil.")


admin.site.register([
    Cor,
    Sexo,
    TipoTelefone,
    TipoEndereco,
    Endereco,
    Telefone,
])
