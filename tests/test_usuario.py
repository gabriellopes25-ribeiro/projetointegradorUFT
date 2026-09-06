import unittest
from src.models.usuario import Usuario, Perfil


class UsuarioTest(unittest.TestCase):
    def test_perfil_padrao_consulta_e_hash_omitido_na_representacao(self):
        usuario = Usuario(id="1", nome="Ana", email="ana@example.com", senha_hash="hash-ficticio")
        self.assertEqual(usuario.perfil, Perfil.CONSULTA)
        self.assertNotIn("hash-ficticio", repr(usuario))
