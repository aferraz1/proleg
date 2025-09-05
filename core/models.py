from __future__ import annotations


from django.conf import settings
from django.db import models


class TimeStamped(models.Model):
    """Abstract base model that tracks creation and modification data."""

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated",
    )
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_deleted",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ("-created_at",)


class Cor(TimeStamped):
    nome = models.CharField(max_length=50)
    codigo = models.CharField(max_length=7)
    descricao = models.TextField(blank=True)

    class Meta:
        verbose_name = "cor"
        verbose_name_plural = "cores"

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return self.nome


class Regiao(TimeStamped):
    id = models.PositiveIntegerField(primary_key=True)
    sigla = models.CharField(max_length=2)
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    malha = models.URLField(blank=True)

    class Meta:
        verbose_name = "região"
        verbose_name_plural = "regiões"
        ordering = ("nome",)

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return self.nome


class Estado(TimeStamped):
    id = models.PositiveIntegerField(primary_key=True)
    sigla = models.CharField(max_length=2)
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    malha = models.URLField(blank=True)
    bandeira = models.ImageField(upload_to="estados/bandeiras/", blank=True)
    brasao = models.ImageField(upload_to="estados/brasoes/", blank=True)
    regiao = models.ForeignKey(Regiao, on_delete=models.PROTECT, related_name="estados")

    class Meta:
        verbose_name = "estado"
        verbose_name_plural = "estados"
        ordering = ("nome",)

    def __str__(self) -> str:  # pragma: no cover
        return self.nome


class Municipio(TimeStamped):
    id = models.PositiveIntegerField(primary_key=True)
    nome = models.CharField(max_length=150)
    malha = models.URLField(blank=True)
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT, related_name="municipios")

    class Meta:
        verbose_name = "município"
        verbose_name_plural = "municípios"
        ordering = ("nome",)

    def __str__(self) -> str:  # pragma: no cover
        return self.nome


class Sexo(TimeStamped):
    sigla = models.CharField(max_length=3, primary_key=True)
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    imagem = models.ImageField(upload_to="sexos/imagens/", blank=True)
    icone = models.ImageField(upload_to="sexos/icones/", blank=True)
    cor = models.ForeignKey(Cor, on_delete=models.PROTECT, related_name="sexos")

    class Meta:
        verbose_name = "sexo"
        verbose_name_plural = "sexos"
        ordering = ("nome",)

    def __str__(self) -> str:  # pragma: no cover
        return self.nome


class TipoTelefone(TimeStamped):
    sigla = models.CharField(max_length=3)
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    imagem = models.ImageField(upload_to="tipos_telefone/imagens/", blank=True)
    icone = models.ImageField(upload_to="tipos_telefone/icones/", blank=True)
    cor = models.ForeignKey(Cor, on_delete=models.PROTECT, related_name="tipos_telefone")

    class Meta:
        verbose_name = "tipo de telefone"
        verbose_name_plural = "tipos de telefone"
        ordering = ("nome",)

    def __str__(self) -> str:  # pragma: no cover
        return self.nome


class TipoEndereco(TimeStamped):
    sigla = models.CharField(max_length=3, unique=True)
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    imagem = models.ImageField(upload_to="tipos_endereco/imagens/", blank=True)
    icone = models.ImageField(upload_to="tipos_endereco/icones/", blank=True)
    cor = models.ForeignKey(Cor, on_delete=models.PROTECT, related_name="tipos_endereco")

    class Meta:
        verbose_name = "tipo de endereço"
        verbose_name_plural = "tipos de endereço"
        ordering = ("nome",)

    def __str__(self) -> str:  # pragma: no cover
        return self.nome


class Endereco(TimeStamped):
    tipo = models.ManyToManyField(TipoEndereco, related_name="enderecos")
    logradouro = models.CharField(max_length=255)
    complemento = models.CharField(max_length=50, blank=True)
    numero = models.CharField(max_length=10)
    bairro = models.CharField(max_length=150)
    municipio = models.ForeignKey(Municipio, on_delete=models.PROTECT, related_name="enderecos")
    cep = models.CharField(max_length=10)
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    ddd = models.PositiveIntegerField(null=True, blank=True)
    anotacoes = models.JSONField(blank=True, default=dict)

    class Meta:
        verbose_name = "endereço"
        verbose_name_plural = "endereços"
        unique_together = (
            "logradouro",
            "numero",
            "complemento",
            "bairro",
            "municipio",
            "cep",
        )

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.logradouro}, {self.numero} - {self.municipio.nome}"


COUNTRY_CHOICES = [
    ("BR", "+55 Brasil"),
    ("US", "+1 Estados Unidos"),
]


class Telefone(TimeStamped):
    tipo = models.ManyToManyField(TipoTelefone, related_name="telefones")
    pais = models.CharField(max_length=2, choices=COUNTRY_CHOICES, default="BR")
    numero = models.CharField(max_length=15)
    ramal = models.CharField(max_length=15, blank=True)

    class Meta:
        verbose_name = "telefone"
        verbose_name_plural = "telefones"
        unique_together = ("pais", "numero", "ramal")

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.pais} {self.numero}"
