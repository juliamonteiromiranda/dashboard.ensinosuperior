
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Dashboard do Ensino Superior",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Dashboard do Ensino Superior")
st.write(
    "Veja quantas instituições de ensino superior existem "
    "por estado, município e categoria no Brasil."
)

st.sidebar.header("Sobre o projeto")
st.sidebar.write("Fonte: Base de instituições de ensino superior do e-MEC.")

arquivo = st.file_uploader(
    "Envie o arquivo CSV",
    type=["csv"]
)


def ler_csv(arquivo):
    for codificacao in ["utf-8-sig", "cp1252", "latin1"]:
        try:
            arquivo.seek(0)
            return pd.read_csv(
                arquivo,
                sep=None,
                engine="python",
                encoding=codificacao
            )
        except (UnicodeDecodeError, pd.errors.ParserError):
            continue

    raise ValueError("Não foi possível ler o arquivo CSV.")


if arquivo is None:
    st.info("Envie o arquivo CSV para visualizar os gráficos.")

else:
    try:
        df = ler_csv(arquivo)

        df.columns = [
            str(coluna).strip().replace("\ufeff", "")
            for coluna in df.columns
        ]

        # Limpar espaços dos textos
        for coluna in df.select_dtypes(include="object").columns:
            df[coluna] = df[coluna].apply(
                lambda valor: valor.strip()
                if isinstance(valor, str)
                else valor
            )

        st.subheader("📊 Informações gerais")

        total_registros = len(df)

        if "CODIGO_DA_IES" in df.columns:
            total_instituicoes = df["CODIGO_DA_IES"].nunique()
        else:
            total_instituicoes = total_registros

        col1, col2 = st.columns(2)

        col1.metric("Registros na planilha", total_registros)
        col2.metric("Códigos de instituições diferentes", total_instituicoes)

        # Considerar apenas instituições ativas, quando houver
        dados = df.copy()

        if "SITUACAO_IES" in dados.columns:
            situacoes = (
                dados["SITUACAO_IES"]
                .dropna()
                .astype(str)
                .str.strip()
                .str.casefold()
            )

            ativas = situacoes.isin(["ativa", "em atividade"])

            if ativas.any():
                somente_ativas = st.checkbox(
                    "Mostrar somente instituições ativas",
                    value=True
                )

                if somente_ativas:
                    dados = dados.loc[ativas].copy()

        st.caption(
            f"Os gráficos abaixo consideram {len(dados)} registros "
            "após a aplicação dos filtros."
        )

        # Contar instituições diferentes
        coluna_contagem = (
            "CODIGO_DA_IES"
            if "CODIGO_DA_IES" in dados.columns
            else "NOME_DA_IES"
        )

        if coluna_contagem not in dados.columns:
            dados["_CONTAGEM"] = 1
            coluna_contagem = "_CONTAGEM"

        # GRÁFICO 1: instituições por estado
        st.divider()
        st.subheader("🗺️ 1. Quantas instituições existem em cada estado?")

        if "UF" in dados.columns:
            por_estado = (
                dados.dropna(subset=["UF"])
                .groupby("UF")[coluna_contagem]
                .nunique()
                .reset_index(name="Quantidade")
                .sort_values("Quantidade", ascending=False)
            )

            fig1 = px.bar(
                por_estado,
                x="UF",
                y="Quantidade",
                text="Quantidade",
                labels={
                    "UF": "Estado",
                    "Quantidade": "Número de instituições"
                },
                title="Instituições de ensino superior por estado"
            )

            fig1.update_traces(textposition="outside")
            fig1.update_layout(showlegend=False)

            st.plotly_chart(fig1, use_container_width=True)

            st.write(
                "Este gráfico mostra quantas instituições estão "
                "cadastradas em cada estado. As barras mais altas "
                "representam estados com mais instituições na base."
            )
        else:
            st.warning("A coluna UF não foi encontrada.")

        # GRÁFICO 2: instituições por município
        st.divider()
        st.subheader("🏙️ 2. Quais municípios têm mais instituições?")

        if "MUNICIPIO" in dados.columns:
            por_municipio = (
                dados.dropna(subset=["MUNICIPIO"])
                .groupby("MUNICIPIO")[coluna_contagem]
                .nunique()
                .reset_index(name="Quantidade")
                .sort_values("Quantidade", ascending=False)
                .head(10)
            )

            fig2 = px.bar(
                por_municipio.sort_values("Quantidade"),
                x="Quantidade",
                y="MUNICIPIO",
                orientation="h",
                text="Quantidade",
                labels={
                    "MUNICIPIO": "Município",
                    "Quantidade": "Número de instituições"
                },
                title="10 municípios com mais instituições"
            )

            fig2.update_traces(textposition="outside")
            fig2.update_layout(showlegend=False)

            st.plotly_chart(fig2, use_container_width=True)

            st.write(
                "Este gráfico apresenta os 10 municípios com mais "
                "instituições cadastradas. Ele facilita a comparação "
                "entre as cidades."
            )
        else:
            st.warning("A coluna MUNICIPIO não foi encontrada.")

        # GRÁFICO 3: instituições públicas e privadas
        st.divider()
        st.subheader("🏫 3. Instituições públicas e privadas")

        if "CATEGORIA_DA_IES" in dados.columns:
            por_categoria = (
                dados.dropna(subset=["CATEGORIA_DA_IES"])
                .groupby("CATEGORIA_DA_IES")[coluna_contagem]
                .nunique()
                .reset_index(name="Quantidade")
                .sort_values("Quantidade", ascending=False)
            )

            fig3 = px.bar(
                por_categoria,
                x="CATEGORIA_DA_IES",
                y="Quantidade",
                text="Quantidade",
                color="CATEGORIA_DA_IES",
                labels={
                    "CATEGORIA_DA_IES": "Categoria",
                    "Quantidade": "Número de instituições"
                },
                title="Quantidade por categoria de instituição"
            )

            fig3.update_traces(textposition="outside")
            fig3.update_layout(showlegend=False)

            st.plotly_chart(fig3, use_container_width=True)

            st.write(
                "Este gráfico compara a quantidade de instituições "
                "públicas e privadas cadastradas na base."
            )
        else:
            st.warning("A coluna CATEGORIA_DA_IES não foi encontrada.")

        # Tabela dos dados
        st.divider()
        st.subheader("📋 Dados da planilha")

        st.dataframe(dados.head(20), use_container_width=True)

        st.download_button(
            "⬇️ Baixar dados analisados",
            data=dados.to_csv(index=False).encode("utf-8-sig"),
            file_name="dados_ensino_superior.csv",
            mime="text/csv"
        )

    except Exception as erro:
        st.error(f"Não foi possível analisar o arquivo: {erro}")

