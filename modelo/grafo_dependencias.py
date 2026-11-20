from .tarefa import Tarefa


class GrafoDependencias:
    def __init__(self) -> None:
        self._tarefas: dict[str, Tarefa] = {}
        self._adjacencias: dict[str, list[str]] = {}

    def adicionarTarefa(self, tarefa: Tarefa) -> None:
        if not isinstance(tarefa, Tarefa):
            raise ValueError("O cadastro exige um objeto Tarefa.")
        if tarefa.id in self._tarefas:
            raise ValueError(f"Já existe uma tarefa com o identificador {tarefa.id!r}.")

        self._tarefas[tarefa.id] = tarefa
        self._adjacencias[tarefa.id] = []

    def adicionarDependencia(self, preRequisito: str, dependente: str) -> None:
        origem = self._validar_id(preRequisito)
        destino = self._validar_id(dependente)

        dependentes = self._adjacencias[origem]
        if destino not in dependentes:
            dependentes.append(destino)

    def removerDependencia(self, preRequisito: str, dependente: str) -> None:
        origem = self._validar_id(preRequisito)
        destino = self._validar_id(dependente)

        dependentes = self._adjacencias[origem]
        if destino not in dependentes:
            raise ValueError(f"A dependência de {origem!r} para {destino!r} não existe.")
        dependentes.remove(destino)

    def obterTarefas(self) -> list[Tarefa]:
        return list(self._tarefas.values())

    def obterDependentes(self, id: str) -> list[str]:
        return self._adjacencias[self._validar_id(id)].copy()

    def calcularGrausEntrada(self) -> dict[str, int]:
        graus = dict.fromkeys(self._tarefas, 0)
        for dependentes in self._adjacencias.values():
            for dependente in dependentes:
                graus[dependente] += 1
        return graus

    def _validar_id(self, id: str) -> str:
        if not isinstance(id, str) or not id.strip():
            raise ValueError("O identificador da tarefa deve ser um texto não vazio.")
        identificador = id.strip()
        if identificador not in self._tarefas:
            raise ValueError(f"Nenhuma tarefa cadastrada com o identificador {identificador!r}.")
        return identificador
