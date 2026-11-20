import unittest

from modelo.grafo_dependencias import GrafoDependencias
from modelo.tarefa import Tarefa
from servicos.simulador_execucao import SimuladorExecucao


class TestSimuladorExecucao(unittest.TestCase):
    def setUp(self) -> None:
        self.grafo = GrafoDependencias()
        self.simulador = SimuladorExecucao()

    def cadastrar(self, *identificadores: str) -> None:
        for identificador in identificadores:
            self.grafo.adicionarTarefa(Tarefa(identificador, f"Tarefa {identificador}"))

    def test_grafo_vazio(self) -> None:
        self.assertEqual(self.simulador.simularExecucao(self.grafo), [])

    def test_tarefas_paralelas_ficam_na_mesma_rodada(self) -> None:
        self.cadastrar("T1", "T2", "T3")
        self.grafo.adicionarDependencia("T1", "T3")
        self.grafo.adicionarDependencia("T2", "T3")

        self.assertEqual(
            self.simulador.simularExecucao(self.grafo),
            [["T1", "T2"], ["T3"]],
        )

    def test_dependente_espera_o_ultimo_pre_requisito(self) -> None:
        self.cadastrar("T1", "T2", "T3")
        self.grafo.adicionarDependencia("T1", "T2")
        self.grafo.adicionarDependencia("T1", "T3")
        self.grafo.adicionarDependencia("T2", "T3")

        self.assertEqual(
            self.simulador.simularExecucao(self.grafo),
            [["T1"], ["T2"], ["T3"]],
        )

    def test_rejeita_grafo_com_ciclo(self) -> None:
        self.cadastrar("T1", "T2")
        self.grafo.adicionarDependencia("T1", "T2")
        self.grafo.adicionarDependencia("T2", "T1")

        with self.assertRaisesRegex(ValueError, "contém um ciclo"):
            self.simulador.simularExecucao(self.grafo)