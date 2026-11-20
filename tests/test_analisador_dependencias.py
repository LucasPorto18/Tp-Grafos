import unittest

from modelo.grafo_dependencias import GrafoDependencias
from modelo.tarefa import Tarefa
from servicos.analisador_dependencias import AnalisadorDependencias


class TestAnalisadorDependencias(unittest.TestCase):
    def setUp(self) -> None:
        self.grafo = GrafoDependencias()
        self.analisador = AnalisadorDependencias()

    def cadastrar(self, *identificadores: str) -> None:
        for identificador in identificadores:
            self.grafo.adicionarTarefa(Tarefa(identificador, f"Tarefa {identificador}"))

    def test_grafo_vazio(self) -> None:
        self.assertIsNone(self.analisador.detectarCiclo(self.grafo))
        self.assertEqual(self.analisador.ordenarTarefas(self.grafo), [])

    def test_grafo_sem_ciclo_com_dois_pre_requisitos(self) -> None:
        self.cadastrar("T3", "T1", "T2", "T4")
        self.grafo.adicionarDependencia("T1", "T3")
        self.grafo.adicionarDependencia("T2", "T3")

        self.assertIsNone(self.analisador.detectarCiclo(self.grafo))
        ordem = self.analisador.ordenarTarefas(self.grafo)
        self.assertIsNotNone(ordem)
        self.assertCountEqual(ordem, ["T1", "T2", "T3", "T4"])
        self.assertLess(ordem.index("T1"), ordem.index("T3"))
        self.assertLess(ordem.index("T2"), ordem.index("T3"))

    def test_ciclo_em_componente_desconectado(self) -> None:
        self.cadastrar("T0", "T1", "T2")
        self.grafo.adicionarDependencia("T1", "T2")
        self.grafo.adicionarDependencia("T2", "T1")

        self.assertEqual(
            self.analisador.detectarCiclo(self.grafo), ["T1", "T2", "T1"]
        )
        self.assertIsNone(self.analisador.ordenarTarefas(self.grafo))

    def test_autodependencia(self) -> None:
        self.cadastrar("T1")
        self.grafo.adicionarDependencia("T1", "T1")

        self.assertEqual(self.analisador.detectarCiclo(self.grafo), ["T1", "T1"])
        self.assertIsNone(self.analisador.ordenarTarefas(self.grafo))