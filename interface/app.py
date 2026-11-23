from pathlib import Path
from tempfile import TemporaryDirectory

import streamlit as st

from aplicacao.controlador_sistema import ControladorSistema


BASE_PROJECT_PLAN = Path(__file__).resolve().parents[1] / "dados" / "T.csv"
EXEMPLO_COM_CICLO = (
    "ID,Task Name,Dependencies\n"
    "T1,Planejar,T2\n"
    "T2,Revisar,T1\n"
)


def main() -> None:
    st.set_page_config(page_title="TP de Grafos", layout="wide")
    st.title("Planejamento de tarefas")

    cenario = st.selectbox(
        "Cenário",
        ["Project Plan (T.csv)", "Exemplo com ciclo"],
    )

    controlador = ControladorSistema()
    try:
        if cenario == "Project Plan (T.csv)":
            resultado = controlador.analisarProjeto(BASE_PROJECT_PLAN)
        else:
            with TemporaryDirectory() as pasta:
                caminho = Path(pasta) / "projeto_com_ciclo.csv"
                caminho.write_text(EXEMPLO_COM_CICLO, encoding="utf-8")
                resultado = controlador.analisarProjeto(caminho)
    except (OSError, ValueError) as erro:
        st.error(f"Não foi possível analisar o CSV. {erro}")
        return

    tarefas, dependencias = st.columns(2)
    tarefas.metric("Tarefas", len(resultado.graus_entrada))
    dependencias.metric("Dependências", sum(resultado.graus_entrada.values()))

    if resultado.ciclo is not None:
        st.error(f"Ciclo encontrado: {' → '.join(resultado.ciclo)}")
        st.write("Resolva o ciclo para gerar uma ordem de execução.")
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

    st.subheader("Pré-requisitos diretos por tarefa")
    st.dataframe(
        [
            {"ID": identificador, "Quantidade": grau}
            for identificador, grau in resultado.graus_entrada.items()
        ],
        hide_index=True,
    )


if __name__ == "__main__":
    main()