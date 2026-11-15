
import pandas as pd
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Recomendador de Ferramentas de IA",
    page_icon="🤖",
    layout="wide"
)

@st.cache_data
def carregar_dados(versao_arquivo):

    caminho = Path(__file__).parent / "ferramentas_ia_enriquecida.csv"
    return pd.read_csv(caminho)

arquivo_dados = Path(__file__).parent / "ferramentas_ia_enriquecida.csv"
df = carregar_dados(arquivo_dados.stat().st_mtime_ns)

TRADUCOES = {
    "text": "Texto",
    "image": "Imagem",
    "video": "Vídeo",
    "audio": "Áudio",
    "code": "Programação",
    "design": "Design",
    "infra": "Infraestrutura",
    "productivity": "Produtividade",
    "safety": "Segurança",
    "multimodal": "Multimodal"
}



def recomendar(
    df,
    modalidades,
    categoria,
    exige_api,
    exige_open_source,
    prefere_api=False,
    prefere_open_source=False
):
    candidatos = df.copy()

    if exige_api:
        candidatos = candidatos[candidatos["api_available"] == 1]

    if exige_open_source:
        candidatos = candidatos[candidatos["open_source"] == 1]

    if candidatos.empty:
        return candidatos

    candidatos = candidatos.copy()

    candidatos["match_modalidade"] = (
        candidatos["modality_canonical"].isin(modalidades).astype(int)
    )

    candidatos["match_categoria"] = (
        (candidatos["category_canonical"] == categoria).astype(int)
        if categoria else 0
    )

    candidatos["match_api"] = (
        candidatos["api_available"].eq(1).astype(int)
    )

    candidatos["match_open_source"] = (
        candidatos["open_source"].eq(1).astype(int)
    )

    # Correspondência com a necessidade
    total_relevancia = (
        len(modalidades) * 40
        + (25 if categoria else 0)
    )

    if total_relevancia == 0:
        return candidatos.iloc[0:0]

    candidatos["score_relevancia"] = (
        candidatos["match_modalidade"] * 40
        + candidatos["match_categoria"] * 25
    )

    candidatos = candidatos[
        candidatos["score_relevancia"] > 0
    ].copy()

    candidatos["relevancia_%"] = (
        100 * candidatos["score_relevancia"] / total_relevancia
    ).round(1)

    # Critérios complementares
    peso_api = 15 if prefere_api else 5
    peso_open_source = 15 if prefere_open_source else 5

    candidatos["score_complementar"] = (
        candidatos["match_api"] * peso_api
        + candidatos["match_open_source"] * peso_open_source
    )

    total_complementar = peso_api + peso_open_source

    candidatos["complementar_%"] = (
        100 * candidatos["score_complementar"]
        / total_complementar
    ).round(1)

    # Relevância domina a pontuação final
    candidatos["score"] = (
        0.85 * candidatos["relevancia_%"]
        + 0.15 * candidatos["complementar_%"]
    )

    candidatos["compatibilidade"] = (
        candidatos["score"].round(1)
    )

    return candidatos.sort_values(
        ["score", "tool_name"],
        ascending=[False, True]
    ).reset_index(drop=True)

st.title("🤖 Recomendador de Ferramentas de IA")
st.write(
    "Encontre ferramentas de inteligência artificial de acordo "
    "com suas necessidades e preferências."
)

st.info(
    "As recomendações são baseadas em metadados de 113 ferramentas. "
    "As modalidades representam classificações principais, "
    "não todas as capacidades reais de cada produto."
)

with st.sidebar:
    st.header("Suas preferências")

    modalidades = st.multiselect(
        "O que você deseja fazer?",
        options=list(TRADUCOES.keys()),
        format_func=lambda x: TRADUCOES[x],
        default=["code"]
    )

    categorias = sorted(df["category_canonical"].dropna().unique())

    categoria_escolhida = st.selectbox(
        "Categoria de interesse (opcional)",
        options=["Todas"] + categorias
    )

    categoria = (
        None if categoria_escolhida == "Todas"
        else categoria_escolhida
    )

    st.markdown("### Preferências")

    prefere_api = st.checkbox(
        "Prefiro ferramentas com API"
    )

    prefere_open_source = st.checkbox(
        "Prefiro ferramentas de código aberto"
    )

    st.markdown("### Requisitos obrigatórios")

    exige_api = st.checkbox("Exigir API disponível")
    exige_open_source = st.checkbox("Exigir código aberto")


    tipo_programacao = "Todos os tipos"

    if "code" in modalidades:
        tipos = sorted(
            df["tipo_ferramenta"].dropna().unique().tolist()
        )

        tipo_programacao = st.selectbox(
            "Tipo de ferramenta de programação",
            ["Todos os tipos"] + tipos,
            help="Classificação funcional preliminar."
        )


    tarefa_programacao = "Qualquer tarefa"

    if "code" in modalidades:
        tarefa_programacao = st.selectbox(
            "Tarefa específica de programação",
            [
                "Qualquer tarefa",
                "Gerar código",
                "Corrigir erros",
                "Explicar código"
            ],
            help="As capacidades foram verificadas apenas para parte do catálogo."
        )

    buscar = st.button("Encontrar ferramentas", type="primary")

if buscar:
    if not modalidades and not categoria:
        st.warning("Selecione pelo menos uma modalidade ou categoria.")
    else:

        df_busca = df.copy()

        if tipo_programacao != "Todos os tipos":
            df_busca = df_busca[
                df_busca["tipo_ferramenta"] == tipo_programacao
            ].copy()

        resultados = recomendar(
            df_busca, modalidades, categoria,
            exige_api, exige_open_source,
            prefere_api=prefere_api,
            prefere_open_source=prefere_open_source
        )

        # Prioridade por capacidade documentada
        mapa_tarefas = {
            "Gerar código": "gera_codigo",
            "Corrigir erros": "depura_codigo",
            "Explicar código": "explica_codigo"
        }

        if (
            tarefa_programacao in mapa_tarefas
            and not resultados.empty
        ):
            coluna_tarefa = mapa_tarefas[tarefa_programacao]

            resultados = resultados.copy()

            resultados["capacidade_confirmada"] = (
                resultados[coluna_tarefa].eq(1).fillna(False)
            )

            resultados = resultados.sort_values(
                by=["capacidade_confirmada", "score", "tool_name"],
                ascending=[False, False, True],
                kind="stable"
            )

            st.info(
                "Ferramentas com a capacidade documentada aparecem primeiro. "
                "As demais podem ter essa capacidade, mas ainda não foram verificadas."
            )


        if resultados.empty:
            st.warning(
                "Nenhuma ferramenta encontrada com os critérios selecionados."
            )
        else:
            st.subheader("Suas recomendações")

            melhor_score = resultados.iloc[0]["score"]
            empatadas = int((resultados["score"] == melhor_score).sum())

            if empatadas > 1:
                st.warning(
                    f"{empatadas} ferramentas empataram na maior pontuação. "
                    "A primeira posição não indica superioridade comprovada."
                )

            for i, (_, ferramenta) in enumerate(
                resultados.head(10).iterrows()
            ):
                with st.container(border=True):
                    if ferramenta["score"] == melhor_score:
                        st.markdown("### ⭐ Entre as mais bem classificadas")
                    else:
                        st.markdown(f"### {i+1}. Alternativa")

                    st.markdown(f"**{ferramenta['tool_name']}**")
                    st.write(f"Empresa: {ferramenta['company']}")
                    st.write(
                        f"Categoria: {ferramenta['category_canonical']}"
                    )
                    st.write(
                        "Modalidade principal: "
                        + TRADUCOES.get(
                            ferramenta["modality_canonical"],
                            ferramenta["modality_canonical"]
                        )
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Pontuação geral",
                            f"{ferramenta['compatibilidade']:.1f}"
                        )

                    with col2:
                        st.metric(
                            "Relevância",
                            f"{ferramenta['relevancia_%']:.1f}%"
                        )

                    with col3:
                        st.metric(
                            "Critérios técnicos",
                            f"{ferramenta['complementar_%']:.1f}%"
                        )

                    st.caption(
                        "Pontuação geral = 85% relevância + "
                        "15% características técnicas. "
                        "É um índice heurístico, não uma "
                        "probabilidade de adequação."
                    )

                    justificativas = []

                    if ferramenta["match_modalidade"]:
                        justificativas.append(
                            "corresponde a uma modalidade selecionada"
                        )

                    if ferramenta["match_categoria"]:
                        justificativas.append(
                            "pertence à categoria desejada"
                        )

                    if prefere_api and ferramenta["match_api"]:
                        justificativas.append("atende à preferência por API")

                    if prefere_open_source and ferramenta["match_open_source"]:
                        justificativas.append(
                            "atende à preferência por código aberto"
                        )

                    if exige_api:
                        justificativas.append("possui API registrada")

                    if exige_open_source:
                        justificativas.append(
                            "é classificada como código aberto"
                        )

                    st.write(
                        "**Por que foi recomendada?** "
                        + "; ".join(justificativas).capitalize() + "."
                    )

                    st.link_button(
                        "Visitar ferramenta",
                        ferramenta["website"]
                    )

            st.caption(
                "As pontuações são calculadas a partir dos metadados "
                "disponíveis. API e código aberto são características "
                "técnicas, não medidas de qualidade. Ferramentas com "
                "pontuações iguais permanecem empatadas."
            )
