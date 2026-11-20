from dataclasses import FrozenInstanceError
import unittest

from modelo.grafo_dependencias import GrafoDependencias
from modelo.tarefa import Tarefa


class TestTarefa(unittest.TestCase):
    def test_normaliza_textos_e_preserva_identificador_como_texto(self):
        tarefa = Tarefa(" 01 ", " Implementar API ")
        self.assertEqual(tarefa.id, "01")
        self.assertEqual(tarefa.nome, "Implementar API")

    def test_rejeita_campos_vazios_ou_que_nao_sejam_texto(self):
        for valor in ("", " \t\n", 1, None):
            with self.subTest(valor=valor, campo="id"):
                with self.assertRaisesRegex(ValueError, "identificador"):
                    Tarefa(valor, "Planejar")
            with self.subTest(valor=valor, campo="nome"):
                with self.assertRaisesRegex(ValueError, "nome"):
                    Tarefa("T1", valor)

    def test_tarefa_e_imutavel(self):
        tarefa = Tarefa("1", "Planejar")
        for campo in ("id", "nome"):
            with self.subTest(campo=campo):
                with self.assertRaises(FrozenInstanceError):
                    setattr(tarefa, campo, "Outro")


class TestGrafoDependencias(unittest.TestCase):
    def setUp(self):
        self.grafo = GrafoDependencias()

    def cadastrar(self, *ids: str) -> list[Tarefa]:
        tarefas = [Tarefa(id, f"Tarefa {id}") for id in ids]
        for tarefa in tarefas:
            self.grafo.adicionarTarefa(tarefa)
        return tarefas

    def test_grafo_inicialmente_vazio(self):
        self.assertEqual(self.grafo.obterTarefas(), [])
        self.assertEqual(self.grafo.calcularGrausEntrada(), {})

    def test_cadastro_em_ordem_e_rejeicao_de_repeticao(self):
        tarefas = self.cadastrar("T2", "1")
        with self.assertRaises(ValueError):
            self.grafo.adicionarTarefa(Tarefa(" T2 ", "Outra"))
        self.assertEqual(self.grafo.obterTarefas(), tarefas)
        self.assertEqual(self.grafo.obterDependentes("T2"), [])
        self.assertEqual(list(self.grafo.calcularGrausEntrada()), ["T2", "1"])

    def test_direcao_ordem_e_multiplos_pre_requisitos(self):
        self.cadastrar("1", "2", "T3", "T4")
        self.grafo.adicionarDependencia(" 1 ", " T4 ")
        self.grafo.adicionarDependencia("1", "T3")
        self.grafo.adicionarDependencia("2", "T3")

        self.assertEqual(self.grafo.obterDependentes(" 1 "), ["T4", "T3"])
        self.assertEqual(self.grafo.obterDependentes("2"), ["T3"])
        self.assertEqual(self.grafo.obterDependentes("T3"), [])
        self.assertEqual(self.grafo.calcularGrausEntrada(), {"1": 0, "2": 0, "T3": 2, "T4": 1})

    def test_duplicar_dependencia_preserva_uma_aresta(self):
        self.cadastrar("1", "2")
        self.grafo.adicionarDependencia("1", "2")
        self.grafo.adicionarDependencia("1", "2")
        self.assertEqual(self.grafo.obterDependentes("1"), ["2"])
        self.assertEqual(self.grafo.calcularGrausEntrada(), {"1": 0, "2": 1})

    def test_remocao_de_dependencia_e_rejeicao_de_aresta_inexistente(self):
        self.cadastrar("1", "2", "3")
        self.grafo.adicionarDependencia("1", "2")
        self.grafo.adicionarDependencia("1", "3")
        self.grafo.removerDependencia(" 1 ", " 2 ")
        with self.assertRaises(ValueError):
            self.grafo.removerDependencia("1", "2")
        self.assertEqual(self.grafo.obterDependentes("1"), ["3"])
        self.assertEqual(self.grafo.calcularGrausEntrada(), {"1": 0, "2": 0, "3": 1})

    def test_referencias_invalidas_preservam_estado(self):
        tarefas = self.cadastrar("1", "2")
        self.grafo.adicionarDependencia("1", "2")
        for invalido in ("T9", " ", 1, None):
            with self.subTest(identificador=invalido):
                with self.assertRaises(ValueError):
                    self.grafo.obterDependentes(invalido)
                for operacao in (self.grafo.adicionarDependencia, self.grafo.removerDependencia):
                    with self.assertRaises(ValueError):
                        operacao(invalido, "2")
                    with self.assertRaises(ValueError):
                        operacao("1", invalido)
        self.assertEqual(self.grafo.obterTarefas(), tarefas)
        self.assertEqual(self.grafo.obterDependentes("1"), ["2"])
        self.assertEqual(self.grafo.obterDependentes("2"), [])
        self.assertEqual(self.grafo.calcularGrausEntrada(), {"1": 0, "2": 1})

    def test_componentes_desconectados_isolamento_ciclo_e_autodependencia(self):
        self.cadastrar("1", "2", "3", "4")
        self.grafo.adicionarDependencia("1", "2")
        self.grafo.adicionarDependencia("2", "1")
        self.grafo.adicionarDependencia("3", "3")
        self.assertEqual(self.grafo.obterDependentes("1"), ["2"])
        self.assertEqual(self.grafo.obterDependentes("2"), ["1"])
        self.assertEqual(self.grafo.obterDependentes("3"), ["3"])
        self.assertEqual(self.grafo.obterDependentes("4"), [])
        self.assertEqual(self.grafo.calcularGrausEntrada(), {"1": 1, "2": 1, "3": 1, "4": 0})

    def test_consultas_devolvem_colecoes_independentes(self):
        tarefas = self.cadastrar("1", "2")
        self.grafo.adicionarDependencia("1", "2")

        self.grafo.obterTarefas().clear()
        self.grafo.obterDependentes("1").clear()
        graus = self.grafo.calcularGrausEntrada()
        graus["2"] = 99

        self.assertEqual(self.grafo.obterTarefas(), tarefas)
        self.assertEqual(self.grafo.obterDependentes("1"), ["2"])
        self.assertEqual(self.grafo.calcularGrausEntrada(), {"1": 0, "2": 1})
