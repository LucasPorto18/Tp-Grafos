from pathlib import Path

from modelo.grafo_dependencias import GrafoDependencias
from modelo.resultado_analise import ResultadoAnalise
from servicos.analisador_dependencias import AnalisadorDependencias
from servicos.carregador_csv import carregar_grafo_csv
from servicos.simulador_execucao import SimuladorExecucao


class ControladorSistema:
    def __init__(self) -> None:
        self._analisador = AnalisadorDependencias()
        self._simulador = SimuladorExecucao()

    def analisarProjeto(self, caminho_csv: str | Path) -> ResultadoAnalise:
        return self.analisarGrafo(carregar_grafo_csv(caminho_csv))

    def analisarGrafo(self, grafo: GrafoDependencias) -> ResultadoAnalise:
        graus_entrada = grafo.calcularGrausEntrada()
        ciclo = self._analisador.detectarCiclo(grafo)

        ordem = None
        rodadas = None
        if ciclo is None:
            ordem = self._analisador.ordenarTarefas(grafo)
            rodadas = self._simulador.simularExecucao(grafo)

        return ResultadoAnalise(
            graus_entrada=graus_entrada,
            ciclo=ciclo,
            ordem_execucao=ordem,
            rodadas=rodadas,
        )