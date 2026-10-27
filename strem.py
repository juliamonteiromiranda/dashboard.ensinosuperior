from pathlib import Path
import unicodedata

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Dashboard do Ensino Superior",
    page_icon="🎓",
    layout="wide"
)

PASTA = Path(__file__).resolve().parent
ARQUIVO_CSV = PASTA / "PDA_Lista_Instituicoes_Ensino_Superior_do_Brasil_EMEC.csv"

st.sidebar.title("Sobre o projeto")
st.sidebar.write("Turma: 2CDD01")
st.sidebar.write("Fonte: Base de instituições de ensino superior do e-MEC.")
st.sidebar.write("Desenvolvido com Python, Pandas, Plotly e Streamlit.")

st.title("🎓 Dashboard do Ensino Superior")
st.header("Turma: 2CDD01")

st.write("**Integrantes do grupo:**")
st.markdown("""
- Priscila Merces
- Eloiza Dias
- Julia Miranda
- Ana Clara Luz
""")

st.divider()

st.write(
    "Este projeto apresenta uma análise de dados sobre as instituições "
    "de ensino superior no Brasil, permitindo visualizar sua distribuição "
    "por estado, município, categoria e situação."
)


def normalizar_coluna(coluna):
    texto = unicodedata.normalize("NFKD", str(coluna))
    texto = texto.encode("ascii", "ignore").decode("ascii")
    return texto.strip().upper().replace(" ", "_")


def normalizar_texto(valor):
    texto = unicodedata.normalize("NFKD", str(valor))
    return texto.encode("ascii", "ignore").decode("ascii").strip().lower()


def carregar_csv(caminho):
    try:
        return pd.read_csv(
            caminho,
            sep=None,
            engine="python",
            encoding="utf-8"
        )
    except UnicodeDecodeError:
        return pd.read_csv(
            caminho,
            sep=None,
            engine="python",
            encoding="latin-1"
        )


if not ARQUIVO_CSV.exists():
    st.error(
        "O arquivo CSV não foi encontrado. Coloque o arquivo "
        "'PDA_Lista_Instituicoes_Ensino_Superior_do_Brasil_EMEC.csv' "
        "na mesma pasta do strem.py."
    )
    st.stop()

try:
    df = carregar_csv(ARQUIVO_CSV)
except Exception as erro:
    st.error(f"Não foi possível abrir o arquivo CSV: {erro}")
    st.stop()

df.columns = [normalizar_coluna(coluna) for coluna in df.columns]
df = df.dropna(how="all")

st.success("Base de dados carregada automaticamente!")

st.subheader("Visão geral dos dados")

col1, col2 = st.columns(2)

col1.metric(
    "Total de registros",
    f"{len(df):,}".replace(",", ".")
)

if "CODIGO_DA_IES" in df.columns:
    total_instituicoes = df["CODIGO_DA_IES"].nunique()
else:
    total_instituicoes = len(df)

col2.metric(
    "Instituições identificadas",
    f"{total_instituicoes:,}".replace(",", ".")
)

if "UF" in df.columns:
    estados = df["UF"].dropna().astype(str).str.strip()
    estados = estados[estados != ""]

    if not estados.empty:
        st.subheader("Quantidade de instituições por estado")

        dados_estado = estados.value_counts().reset_index()
        dados_estado.columns = ["Estado", "Quantidade"]

        fig_estado = px.bar(
            dados_estado,
            x="Estado",
            y="Quantidade",
            title="Instituições de ensino superior por estado",
            labels={
                "Estado": "Estado",
                "Quantidade": "Quantidade de registros"
            }
        )

        st.plotly_chart(fig_estado, use_container_width=True)

        st.write(
            f"O estado com mais registros é **{dados_estado.iloc[0]['Estado']}**, "
            f"com **{dados_estado.iloc[0]['Quantidade']}** registros."
        )

if "MUNICIPIO" in df.columns:
    municipios = df["MUNICIPIO"].dropna().astype(str).str.strip()
    municipios = municipios[municipios != ""]

    if not municipios.empty:
        st.subheader("Municípios com mais instituições")

        dados_municipio = municipios.value_counts().head(10).reset_index()
        dados_municipio.columns = ["Município", "Quantidade"]

        fig_municipio = px.bar(
            dados_municipio,
            x="Quantidade",
            y="Município",
            orientation="h",
            title="10 municípios com mais registros",
            labels={
                "Município": "Município",
                "Quantidade": "Quantidade de registros"
            }
        )

        fig_municipio.update_layout(
            yaxis={"categoryorder": "total ascending"}
        )

        st.plotly_chart(fig_municipio, use_container_width=True)

if "CATEGORIA_DA_IES" in df.columns:
    categorias = df["CATEGORIA_DA_IES"].dropna().astype(str).str.strip()
    categorias = categorias[categorias != ""]

    if not categorias.empty:
        st.subheader("Instituições por categoria")

        dados_categoria = categorias.value_counts().reset_index()
        dados_categoria.columns = ["Categoria", "Quantidade"]

        fig_categoria = px.pie(
            dados_categoria,
            names="Categoria",
            values="Quantidade",
            title="Distribuição por categoria"
        )

        st.plotly_chart(fig_categoria, use_container_width=True)

        st.write(
            f"A categoria com mais registros é "
            f"**{dados_categoria.iloc[0]['Categoria']}**, "
            f"com **{dados_categoria.iloc[0]['Quantidade']}** registros."
        )

if "SITUACAO_IES" in df.columns:
    situacoes = df["SITUACAO_IES"].dropna().astype(str).str.strip()

    def classificar_situacao(valor):
        texto = normalizar_texto(valor)

        if "desativ" in texto or "extint" in texto or "encerrad" in texto:
            return "Desativada"

        if "ativ" in texto:
            return "Ativa"

        return None

    df["SITUACAO_RESUMIDA"] = situacoes.reindex(df.index).map(classificar_situacao)

    situacoes_resumidas = df["SITUACAO_RESUMIDA"].dropna()

    if not situacoes_resumidas.empty:
        st.subheader("Situação das instituições")

        dados_situacao = (
            situacoes_resumidas.value_counts()
            .reindex(["Ativa", "Desativada"], fill_value=0)
            .rename_axis("Situação")
            .reset_index(name="Quantidade")
        )

        fig_situacao = px.bar(
            dados_situacao,
            x="Situação",
            y="Quantidade",
            color="Situação",
            title="Instituições ativas e desativadas",
            category_orders={"Situação": ["Ativa", "Desativada"]},
            labels={
                "Situação": "Situação",
                "Quantidade": "Quantidade de instituições"
            }
        )

        st.plotly_chart(fig_situacao, use_container_width=True)

        total_ativas = int(
            dados_situacao.loc[
                dados_situacao["Situação"] == "Ativa", "Quantidade"
            ].iloc[0]
        )

        total_desativadas = int(
            dados_situacao.loc[
                dados_situacao["Situação"] == "Desativada", "Quantidade"
            ].iloc[0]
        )

        col1, col2 = st.columns(2)
        col1.metric("Ativas", f"{total_ativas:,}".replace(",", "."))
        col2.metric("Desativadas", f"{total_desativadas:,}".replace(",", "."))

st.divider()

st.header("Análise Detalhada dos Resultados")

st.subheader("1. Qual informação aparece?")
st.write(
    f"A base contém {len(df)} registros relacionados às instituições "
    "de ensino superior. Os gráficos mostram sua distribuição por estado, "
    "município, categoria e situação."
)

st.subheader("2. Qual é o maior valor?")
if "UF" in df.columns and not df["UF"].dropna().empty:
    contagem_estados = df["UF"].dropna().astype(str).str.strip().value_counts()
    st.write(
        f"O estado com mais registros é **{contagem_estados.index[0]}**, "
        f"com **{contagem_estados.iloc[0]}** registros."
    )
else:
    st.write("Não há dados de estado disponíveis para essa comparação.")

st.subheader("3. Existe algum valor muito diferente?")
st.write(
    "Os gráficos permitem identificar estados ou municípios com quantidades "
    "maiores ou menores que as demais. Essa diferença não significa "
    "necessariamente que exista um erro nos dados."
)

st.subheader("4. Existe aumento ou diminuição?")
st.write(
    "A análise mostra principalmente a distribuição das instituições. "
    "Para verificar aumento ou diminuição ao longo do tempo, seria necessário "
    "comparar dados de diferentes anos."
)

st.subheader("5. Existem diferenças entre categorias?")
if "CATEGORIA_DA_IES" in df.columns and not df["CATEGORIA_DA_IES"].dropna().empty:
    contagem_categorias = (
        df["CATEGORIA_DA_IES"].dropna().astype(str).str.strip().value_counts()
    )
    st.write(
        f"Sim. A categoria mais frequente é **{contagem_categorias.index[0]}**, "
        f"com {contagem_categorias.iloc[0]} registros."
    )
else:
    st.write("Não foi possível comparar as categorias com os dados disponíveis.")

st.subheader("6. Existe algum padrão aparente?")
st.write(
    "Os gráficos permitem comparar a distribuição dos registros entre estados, "
    "municípios e categorias, ajudando a identificar padrões nos dados."
)

st.subheader("7. Onde a Inteligência Artificial nos ajudou?")
st.write(
    "A Inteligência Artificial ajudou a organizar o código, identificar erros, "
    "tratar os dados e criar gráficos para facilitar a interpretação dos resultados."
)

st.divider()

st.header("Sobre o Projeto")

st.subheader("1. O que investigamos?")
st.write(
    "Investigamos como as instituições de ensino superior estão distribuídas "
    "pelo Brasil, considerando estado, município, categoria e situação."
)

st.subheader("2. Qual base utilizamos?")
st.write(
    "Utilizamos uma base de dados de instituições de ensino superior "
    "do e-MEC, sistema relacionado ao Ministério da Educação."
)

st.subheader("3. O que os dados mostraram?")
st.write(
    "Os dados permitem observar diferenças na distribuição dos registros "
    "entre estados, municípios e categorias de instituições."
)

st.subheader("4. Onde a Inteligência Artificial ajudou?")

st.markdown("""
**Resolução de erros e estruturação:** ajudou a corrigir problemas no código.

**Limpeza e tratamento de dados:** ajudou a organizar as informações utilizadas na análise.

**Síntese de resultados:** ajudou a interpretar os gráficos e apresentar os resultados de forma mais simples.
""")

with st.expander("Visualizar tabela de dados"):
    st.dataframe(df, use_container_width=True)
