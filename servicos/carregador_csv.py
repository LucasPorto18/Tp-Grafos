import csv
from pathlib import Path

from modelo.grafo_dependencias import GrafoDependencias
from modelo.tarefa import Tarefa


def carregar_grafo_csv(caminho: str | Path) -> GrafoDependencias:
    """Carrega tarefas e dependências de um CSV no formato Project Plan."""
    grafo = GrafoDependencias()
    dependencias: list[tuple[int, str, str]] = []

    with open(caminho, encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo, strict=True)
        campos = ("ID", "Task Name", "Dependencies")
        try:
            cabecalho = leitor.fieldnames or []
            ausentes = [campo for campo in campos if campo not in cabecalho]
            if ausentes:
                raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(ausentes)}.")

            for linha in leitor:
                numero = leitor.line_num
                try:
                    if None in linha or any(valor is None for valor in linha.values()):
                        raise ValueError("A quantidade de campos difere do cabeçalho.")
                    tarefa = Tarefa(linha["ID"], linha["Task Name"])
                    grafo.adicionarTarefa(tarefa)
                    campo = linha["Dependencies"].strip()
                    if campo and campo != "-":
                        for identificador in campo.split(","):
                            dependencias.append((numero, identificador.strip(), tarefa.id))
                except ValueError as erro:
                    raise ValueError(f"Linha {numero}: {erro}") from erro
        except csv.Error as erro:
            raise ValueError(f"CSV inválido na linha {leitor.line_num}: {erro}") from erro

    # Todas as tarefas já existem, inclusive as citadas antes do seu cadastro.
    for numero, pre_requisito, dependente in dependencias:
        try:
            grafo.adicionarDependencia(pre_requisito, dependente)
        except ValueError as erro:
            raise ValueError(f"Linha {numero}, dependente {dependente!r}: {erro}") from erro

    return grafo