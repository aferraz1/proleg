from django.test import TestCase

from core.models import Estado, Municipio, Regiao
from core.services import ibge


class IBGEServiceTests(TestCase):
    def test_sync_regioes(self):
        regioes = ibge.sync_regioes(verify=False)
        self.assertGreaterEqual(Regiao.objects.count(), 5)
        self.assertEqual(regioes[0].__class__, Regiao)

    def test_sync_estados(self):
        ibge.sync_regioes(regiao_id=3, verify=False)
        estados = ibge.sync_estados(regiao_id=3, verify=False)
        self.assertTrue(Estado.objects.filter(sigla="SP").exists())
        self.assertEqual(estados[0].regiao.sigla, "SE")

    def test_sync_municipio(self):
        ibge.sync_estados(estado_id=35, verify=False)
        municipio = ibge.sync_municipios(municipio_id=3550308, verify=False)[0]
        self.assertEqual(municipio.nome, "São Paulo")
        self.assertEqual(municipio.estado.sigla, "SP")
