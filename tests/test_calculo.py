import unittest
from src.services.calculo_service import CalculoService


class CalculoTest(unittest.TestCase):
    def test_contrato_nao_pode_ser_usado_como_calculo_pronto(self):
        with self.assertRaises(TypeError):
            CalculoService()

    @unittest.skip("RF05 planejado: fórmula e implementação ainda pendentes")
    def test_calculo_conforme_formula_aprovada(self):
        pass
