from pathlib import Path

import streamlit as st

from aplicacao.controlador_sistema import ControladorSistema
from modelo.grafo_dependencias import GrafoDependencias
from modelo.resultado_analise import ResultadoAnalise
from modelo.tarefa import Tarefa


BASE_PROJECT_PLAN = Path(__file__).resolve().parents[1] / "dados" / "T.csv"


def criar_exemplo_com_ciclo() -> GrafoDependencias:
    grafo = GrafoDependencias()
    grafo.adicionarTarefa(Tarefa("T1", "Planejar"))
    grafo.adicionarTarefa(Tarefa("T2", "Revisar"))
    grafo.adicionarDependencia("T1", "T2")
    grafo.adicionarDependencia("T2", "T1")
    return grafo


def exibir_resultado(resultado: ResultadoAnalise) -> None:
    st.subheader("Resultado da análise")

    tarefas, dependencias = st.columns(2)
    tarefas.metric("Tarefas", len(resultado.graus_entrada))
    dependencias.metric("Dependências", sum(resultado.graus_entrada.values()))

    if resultado.ciclo is not None:
        st.error(f"Ciclo encontrado: {' → '.join(resultado.ciclo)}")
        st.write("Remova uma dependência do ciclo para liberar a execução.")
    elif resultado.ordem_execucao:
        st.subheader("Ordem de execução")
        st.write(" → ".join(resultado.ordem_execucao))

        st.subheader("Simulação por rodadas")
        st.table(
            [
                {"Rodada": numero, "Tarefas": ", ".join(ids)}
                for numero, ids in enumerate(resultado.rodadas or [], start=1)
            ]
        )
    else:
        st.info("O projeto está vazio.")

    if resultado.graus_entrada:
        st.subheader("Pré-requisitos diretos por tarefa")
        st.dataframe(
            [
                {"ID": identificador, "Quantidade": grau}
                for identificador, grau in resultado.graus_entrada.items()
            ],
            hide_index=True,
        )


def editar_grafo(controlador: ControladorSistema) -> None:
    if "grafo_manual" not in st.session_state:
        st.session_state.grafo_manual = GrafoDependencias()
        st.session_state.resultado_manual = None

    grafo = st.session_state.grafo_manual

    with st.form("cadastro_tarefa", clear_on_submit=True):
        st.subheader("Adicionar tarefa")
        identificador = st.text_input("ID", placeholder="T1")
        nome = st.text_input("Nome da tarefa", placeholder="Planejar")
        cadastrar = st.form_submit_button("Adicionar tarefa")

    if cadastrar:
        try:
            grafo.adicionarTarefa(Tarefa(identificador, nome))
        except ValueError as erro:
            st.error(str(erro))
        else:
            st.session_state.resultado_manual = None
            st.success(f"Tarefa {identificador.strip()} adicionada.")

    tarefas = grafo.obterTarefas()
    if not tarefas:
        st.info("Adicione uma tarefa para começar.")
        return

    nomes = {tarefa.id: tarefa.nome for tarefa in tarefas}

    st.subheader("Tarefas cadastradas")
    st.dataframe(
        [{"ID": tarefa.id, "Nome": tarefa.nome} for tarefa in tarefas],
        hide_index=True,
    )

    with st.form("cadastro_dependencia"):
        st.subheader("Adicionar dependência")
        st.caption("Exemplo: se T2 depende de T1, escolha T1 como pré-requisito.")
        pre_requisito = st.selectbox(
            "Pré-requisito",
            options=list(nomes),
            format_func=lambda id: f"{id} · {nomes[id]}",
        )
        dependente = st.selectbox(
            "Tarefa dependente",
            options=list(nomes),
            format_func=lambda id: f"{id} · {nomes[id]}",
        )
        adicionar = st.form_submit_button("Adicionar dependência")

    if adicionar:
        if dependente in grafo.obterDependentes(pre_requisito):
            st.info("Essa dependência já está cadastrada.")
        else:
            grafo.adicionarDependencia(pre_requisito, dependente)
            st.session_state.resultado_manual = None
            st.success(f"Dependência adicionada: {pre_requisito} → {dependente}.")

    arestas = [
        (tarefa.id, destino)
        for tarefa in tarefas
        for destino in grafo.obterDependentes(tarefa.id)
    ]

    if arestas:
        with st.form("remocao_dependencia"):
            st.subheader("Dependências cadastradas")
            origem, destino = st.selectbox(
                "Escolha uma dependência para remover",
                options=arestas,
                format_func=lambda aresta: f"{aresta[0]} → {aresta[1]}",
            )
            remover = st.form_submit_button("Remover dependência")

        if remover:
            grafo.removerDependencia(origem, destino)
            st.session_state.resultado_manual = None
            st.rerun()

    if st.button("Pronto, analisar grafo", type="primary"):
        st.session_state.resultado_manual = controlador.analisarGrafo(grafo)

    resultado = st.session_state.resultado_manual
    if resultado is not None:
        exibir_resultado(resultado)


def main() -> None:
    st.set_page_config(page_title="TP de Grafos", layout="wide")
    st.title("Planejamento de tarefas")

    cenario = st.selectbox(
        "Cenário",
        ["Montar meu grafo", "Project Plan (T.csv)", "Exemplo com ciclo"],
    )
    controlador = ControladorSistema()

    if cenario == "Montar meu grafo":
        editar_grafo(controlador)
        return

    try:
        if cenario == "Project Plan (T.csv)":
            resultado = controlador.analisarProjeto(BASE_PROJECT_PLAN)
        else:
            resultado = controlador.analisarGrafo(criar_exemplo_com_ciclo())
    except (OSError, ValueError) as erro:
        st.error(f"Não foi possível analisar o projeto. {erro}")
        return

    exibir_resultado(resultado)


if __name__ == "__main__":
    main()