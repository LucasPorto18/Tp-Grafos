import json

from modelo.grafo_dependencias import GrafoDependencias


def gerar_dot(grafo: GrafoDependencias, ciclo: list[str] | None = None) -> str:
    """Gera a descrição do diagrama a partir da lista de adjacência."""
    caminho = ciclo or []
    arestas_do_ciclo = set(zip(caminho, caminho[1:]))
    tarefas = grafo.obterTarefas()
    vertices = {tarefa.id: f"v{indice}" for indice, tarefa in enumerate(tarefas)}

    linhas = [
        "digraph dependencias {",
        "  rankdir=LR;",
        '  node [shape=box, style="rounded,filled", fillcolor="#eff6ff", color="#64748b", fontcolor="#0f172a"];',
        '  edge [color="#64748b"];',
    ]

    for tarefa in tarefas:
        rotulo = json.dumps(f"{tarefa.id} — {tarefa.nome}", ensure_ascii=False)
        linhas.append(f"  {vertices[tarefa.id]} [label={rotulo}];")

    for tarefa in tarefas:
        for destino in grafo.obterDependentes(tarefa.id):
            estilo = ""
            if (tarefa.id, destino) in arestas_do_ciclo:
                estilo = ' [color="#dc2626", penwidth=3]'
            linhas.append(f"  {vertices[tarefa.id]} -> {vertices[destino]}{estilo};")

    linhas.append("}")
    return "\n".join(linhas)
