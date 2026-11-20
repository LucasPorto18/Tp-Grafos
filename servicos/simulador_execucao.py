from modelo.grafo_dependencias import GrafoDependencias
from servicos.analisador_dependencias import AnalisadorDependencias


class SimuladorExecucao:
    def simularExecucao(self, grafo: GrafoDependencias) -> list[list[str]]:
        """Agrupa as tarefas em rodadas, respeitando os pré-requisitos."""
        ordem = AnalisadorDependencias().ordenarTarefas(grafo)
        if ordem is None:
            raise ValueError("Não é possível simular a execução: o grafo contém um ciclo.")

        rodada_por_tarefa = dict.fromkeys(ordem, 0)
        rodadas: list[list[str]] = []

        for tarefa in ordem:
            rodada = rodada_por_tarefa[tarefa]
            if rodada == len(rodadas):
                rodadas.append([])
            rodadas[rodada].append(tarefa)

            # Cada dependente espera a rodada do seu último pré-requisito.
            for dependente in grafo.obterDependentes(tarefa):
                rodada_por_tarefa[dependente] = max(
                    rodada_por_tarefa[dependente], rodada + 1
                )

        return rodadas
    