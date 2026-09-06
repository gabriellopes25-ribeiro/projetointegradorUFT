import unittest
from dataclasses import FrozenInstanceError
from decimal import Decimal
from src.models.tributo import Tributo


class TributoTest(unittest.TestCase):
    def test_tributo_preserva_decimal_e_impede_mutacao_acidental(self):
        tributo = Tributo(id="1", nome="IPTU", categoria="Imobiliário", aliquota_base=Decimal("1.25"))
        self.assertEqual(tributo.aliquota_base, Decimal("1.25"))
        with self.assertRaises(FrozenInstanceError):
            tributo.aliquota_base = Decimal("2")

    def test_rejeita_textos_ausentes_ou_invalidos(self):
        for campo in ("id", "nome", "categoria"):
            for valor in ("", "   ", None, 123):
                with self.subTest(campo=campo, valor=valor):
                    dados = dict(id="1", nome="IPTU", categoria="Imobiliário",
                                 aliquota_base=Decimal("1.25"))
                    dados[campo] = valor
                    with self.assertRaisesRegex(ValueError, campo):
                        Tributo(**dados)

    def test_rejeita_aliquota_negativa_nao_finita_ou_tipo_incorreto(self):
        valores = (Decimal("-1"), Decimal("NaN"), Decimal("sNaN"),
                   Decimal("Infinity"), Decimal("-Infinity"), 1.25, "1.25", None)
        for valor in valores:
            with self.subTest(valor=valor):
                with self.assertRaisesRegex(ValueError, "Alíquota base"):
                    Tributo(id="1", nome="IPTU", categoria="Imobiliário",
                            aliquota_base=valor)

    def test_aceita_aliquota_zero(self):
        tributo = Tributo(id="1", nome="IPTU", categoria="Imobiliário",
                          aliquota_base=Decimal("0"))
        self.assertEqual(tributo.aliquota_base, Decimal("0"))
