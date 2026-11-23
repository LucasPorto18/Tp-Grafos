from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from aplicacao.controlador_sistema import ControladorSistema


class TestControladorSistema(unittest.TestCase):
    def setUp(self) -> None:
        self.controlador = ControladorSistema()

    def test_analisa_base_project_plan(self) -> None:
        caminho = Path(__file__).resolve().parents[1] / "dados" / "T.csv"
        resultado = self.controlador.analisarProjeto(caminho)

        self.assertEqual(len(resultado.graus_entrada), 20)
        self.assertEqual(sum(resultado.graus_entrada.values()), 30)
        self.assertIsNone(resultado.ciclo)

        ordem = resultado.ordem_execucao
        rodadas = resultado.rodadas
        if ordem is None or rodadas is None:
            self.fail("A base Project Plan deve gerar uma ordem e rodadas.")

        self.assertCountEqual(ordem, resultado.graus_entrada.keys())
        self.assertCountEqual(
            [tarefa for rodada in rodadas for tarefa in rodada],
            resultado.graus_entrada.keys(),
        )
        self.assertLess(ordem.index("1"), ordem.index("3"))
        self.assertLess(ordem.index("2"), ordem.index("3"))

    def test_informa_ciclo_e_bloqueia_simulacao(self) -> None:
        with TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "projeto_com_ciclo.csv"
            caminho.write_text(
                "ID,Task Name,Dependencies\n"
                "T1,Planejar,T2\n"
                "T2,Revisar,T1\n",
                encoding="utf-8",
            )
            resultado = self.controlador.analisarProjeto(caminho)

        self.assertEqual(resultado.graus_entrada, {"T1": 1, "T2": 1})
        self.assertEqual(resultado.ciclo, ["T1", "T2", "T1"])
        self.assertIsNone(resultado.ordem_execucao)
        self.assertIsNone(resultado.rodadas)