from collections import deque

from modelo.grafo_dependencias import GrafoDependencias


class AnalisadorDependencias:
    def detectarCiclo(self, grafo: GrafoDependencias) -> list[str] | None:
        """Retorna o primeiro ciclo encontrado por DFS, ou None."""
        concluidas: set[str] = set()
        caminho: list[str] = []
        posicoes_no_caminho: dict[str, int] = {}

        def visitar(identificador: str) -> list[str] | None:
            posicoes_no_caminho[identificador] = len(caminho)
            caminho.append(identificador)

            for dependente in grafo.obterDependentes(identificador):
                # Uma aresta para uma tarefa no caminho atual fecha um ciclo.
                if dependente in posicoes_no_caminho:
                    inicio = posicoes_no_caminho[dependente]
                    return caminho[inicio:] + [dependente]

                if dependente not in concluidas:
                    ciclo = visitar(dependente)
                    if ciclo is not None:
                        return ciclo

            caminho.pop()
            del posicoes_no_caminho[identificador]
            concluidas.add(identificador)
            return None

        for tarefa in grafo.obterTarefas():
            if tarefa.id not in concluidas:
                ciclo = visitar(tarefa.id)
                if ciclo is not None:
                    return ciclo

        return None

    def ordenarTarefas(self, grafo: GrafoDependencias) -> list[str] | None:
        """Retorna uma ordem válida pelo algoritmo de Kahn, ou None."""
        graus = grafo.calcularGrausEntrada()
        prontas = deque(
            identificador for identificador, grau in graus.items() if grau == 0
        )
        ordem: list[str] = []

        while prontas:
            tarefa = prontas.popleft()
            ordem.append(tarefa)

            for dependente in grafo.obterDependentes(tarefa):
                graus[dependente] -= 1
                if graus[dependente] == 0:
                    prontas.append(dependente)

        # Se sobraram tarefas, existe pelo menos um ciclo no grafo.
        if len(ordem) != len(graus):
            return None

        return ordem