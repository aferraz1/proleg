"""Forms for interacting with core models and search utilities."""

from __future__ import annotations

from django import forms
from django.core.validators import RegexValidator

from .models import Regiao, Estado, Municipio, Cor, Sexo, TipoTelefone, TipoEndereco, Endereco, Telefone


# Model forms --------------------------------------------------------------

class RegiaoForm(forms.ModelForm):
    class Meta:
        model = Regiao
        fields = "__all__"


class EstadoForm(forms.ModelForm):
    sigla = forms.CharField(
        max_length=2,
        validators=[RegexValidator(r"^[A-Z]{2}$", "Use duas letras maiúsculas")],
        widget=forms.TextInput(attrs={"class": "text-uppercase"}),
    )

    class Meta:
        model = Estado
        fields = "__all__"

    def clean_sigla(self):
        return self.cleaned_data["sigla"].upper()


class MunicipioForm(forms.ModelForm):
    estado = forms.ModelChoiceField(queryset=Estado.objects.all())

    class Meta:
        model = Municipio
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        regiao = kwargs.pop("regiao", None)
        super().__init__(*args, **kwargs)
        if regiao:
            self.fields["estado"].queryset = Estado.objects.filter(regiao=regiao)


class CorForm(forms.ModelForm):
    class Meta:
        model = Cor
        fields = "__all__"


class SexoForm(forms.ModelForm):
    class Meta:
        model = Sexo
        fields = "__all__"


class TipoTelefoneForm(forms.ModelForm):
    class Meta:
        model = TipoTelefone
        fields = "__all__"


class TipoEnderecoForm(forms.ModelForm):
    class Meta:
        model = TipoEndereco
        fields = "__all__"


class EnderecoForm(forms.ModelForm):
    cep = forms.CharField(
        validators=[
            RegexValidator(r"^\d{5}-?\d{3}$", "Informe um CEP válido"),
        ]
    )

    class Meta:
        model = Endereco
        fields = "__all__"


class TelefoneForm(forms.ModelForm):
    numero = forms.CharField(
        validators=[RegexValidator(r"^\d+$", "Use apenas números")]
    )

    class Meta:
        model = Telefone
        fields = "__all__"


# Filter/search utilities --------------------------------------------------

class LocalidadeSearchForm(forms.Form):
    """Simple form to filter ``Municipio`` querysets."""

    nome = forms.CharField(
        required=False,
        label="Nome",
        widget=forms.TextInput(attrs={"placeholder": "Buscar"}),
    )
    regiao = forms.ModelChoiceField(
        queryset=Regiao.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    estado = forms.ModelChoiceField(
        queryset=Estado.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        regiao = self.data.get("regiao") or self.initial.get("regiao")
        if regiao:
            self.fields["estado"].queryset = Estado.objects.filter(regiao_id=regiao)
        else:
            self.fields["estado"].queryset = Estado.objects.all()

    def clean_nome(self):
        return self.cleaned_data["nome"].strip()

    def filter_queryset(self, qs):
        if self.cleaned_data.get("nome"):
            qs = qs.filter(nome__icontains=self.cleaned_data["nome"])
        if self.cleaned_data.get("regiao"):
            qs = qs.filter(estado__regiao=self.cleaned_data["regiao"])
        if self.cleaned_data.get("estado"):
            qs = qs.filter(estado=self.cleaned_data["estado"])
        return qs

