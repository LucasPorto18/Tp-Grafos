from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from servicos.carregador_csv import carregar_grafo_csv


class TestCarregadorCSV(unittest.TestCase):
    def carregar_texto(self, conteudo: str):
        with TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "projeto.csv"
            caminho.write_text(conteudo, encoding="utf-8-sig")
            return carregar_grafo_csv(caminho)

    def test_carrega_base_project_plan(self):
        caminho = Path(__file__).resolve().parents[1] / "dados" / "T.csv"
        grafo = carregar_grafo_csv(caminho)
        tarefas = grafo.obterTarefas()
        graus = grafo.calcularGrausEntrada()

        self.assertEqual(len(tarefas), 20)
        self.assertEqual(sum(graus.values()), 30)
        self.assertEqual((tarefas[0].id, tarefas[0].nome), ("1", "Requirement Gathering"))
        self.assertEqual(grafo.obterDependentes("1"), ["2", "3", "4", "5"])
        self.assertEqual(graus["1"], 0)
        self.assertEqual(graus["3"], 2)

    def test_aceita_referencia_a_tarefa_cadastrada_depois(self):
        grafo = self.carregar_texto(
            'ID,Task Name,Dependencies\n'
            'T3,"Testar, validar","01, T2, 01"\n'
            '01,Planejar,-\n'
            'T2,Implementar,\n'
        )
        self.assertEqual(grafo.obterTarefas()[0].nome, "Testar, validar")
        self.assertEqual(grafo.calcularGrausEntrada(), {"T3": 2, "01": 0, "T2": 0})
        self.assertEqual(grafo.obterDependentes("01"), ["T3"])

    def test_rejeita_coluna_ausente(self):
        with self.assertRaisesRegex(ValueError, "Colunas obrigatórias ausentes.*Dependencies"):
            self.carregar_texto("ID,Task Name\n1,Planejar\n")

    def test_rejeita_linha_incompleta(self):
        with self.assertRaisesRegex(ValueError, "Linha 2.*quantidade de campos"):
            self.carregar_texto("ID,Task Name,Dependencies\n1,Planejar\n")

    def test_rejeita_aspas_invalidas(self):
        with self.assertRaisesRegex(ValueError, "CSV inválido"):
            self.carregar_texto('ID,Task Name,Dependencies\n1,"Planejar,-\n')

    def test_rejeita_id_repetido(self):
        with self.assertRaisesRegex(ValueError, "Linha 3.*Já existe"):
            self.carregar_texto("ID,Task Name,Dependencies\n1,Planejar,-\n1,Revisar,-\n")

    def test_rejeita_pre_requisito_inexistente(self):
        with self.assertRaisesRegex(ValueError, "Linha 2.*dependente '1'.*'99'"):
            self.carregar_texto("ID,Task Name,Dependencies\n1,Planejar,99\n")