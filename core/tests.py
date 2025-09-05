from django.test import SimpleTestCase

from core.services import ibge


class IBGEServiceTests(SimpleTestCase):
    def test_get_regioes(self):
        regioes = ibge.get_regioes(verify=False)
        self.assertIsInstance(regioes, list)
        self.assertGreaterEqual(len(regioes), 5)
        self.assertIn("id", regioes[0])
        self.assertIn("nome", regioes[0])

    def test_get_estado(self):
        sp = ibge.get_estados(estado_id=35, verify=False)
        self.assertIsInstance(sp, dict)
        self.assertEqual(sp["id"], 35)
        self.assertEqual(sp["sigla"], "SP")

    def test_get_municipios_by_estado(self):
        municipios = ibge.get_municipios(estado_id=35, verify=False)
        self.assertIsInstance(municipios, list)
        self.assertGreater(len(municipios), 10)
        self.assertIn("id", municipios[0])
        self.assertIn("nome", municipios[0])
