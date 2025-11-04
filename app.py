# app.py
# Streamlit app para análise de representatividade por fila e hora

import streamlit as st
import pandas as pd
import numpy as np
import io

st.set_page_config(page_title="Representatividade por Fila", layout="wide")

st.title("📊 Representatividade por Fila e Hora")
st.write(
    "Envie o arquivo Excel com os dados por fila/hora "
    "(pode ser o arquivo bruto de entrantes ou já em quantidade)."
)

uploaded_file = st.file_uploader("📂 Envie o arquivo Excel", type=["xlsx"])

if uploaded_file is not None:
    # Lê o Excel (primeira aba)
    df_raw = pd.read_excel(uploaded_file)

    # Confere se existe a coluna Hour
    if "Hour" not in df_raw.columns:
        st.error("A coluna 'Hour' não foi encontrada no arquivo.")
    else:
        # Remove coluna Queue se existir (é só rótulo)
        if "Queue" in df_raw.columns:
            df = df_raw.drop(columns=["Queue"])
        else:
            df = df_raw.copy()

        # 🔎 PRÉVIA: mostra todas as linhas
        st.subheader("📋 Prévia dos Dados")
        st.dataframe(df, use_container_width=True)

        # Identifica colunas de filas (todas menos Hour e qualquer coluna com 'total')
        total_cols = [c for c in df.columns if "total" in c.lower()]
        cols_excluir = ["Hour"] + total_cols
        fila_cols = [c for c in df.columns if c not in cols_excluir]

        if not fila_cols:
            st.warning("Não foram encontradas colunas de filas (apenas 'Hour' e/ou totais).")
        else:
            # ==========================
            # 1) RESULTADO GERAL (TODAS AS HORAS)
            # ==========================

            # Converte todas as colunas de filas para número
            df_filas_num_global = df[fila_cols].apply(pd.to_numeric, errors="coerce")

            # Total por hora (linha)
            total_hora_global = df_filas_num_global.sum(axis=1)

            # Percentual por fila em cada hora
            percent_global = df_filas_num_global.div(
                total_hora_global.replace(0, np.nan), axis=0
            ) * 100

            # DataFrame geral com Hour + filas
            df_percent_global = pd.concat(
                [df["Hour"].reset_index(drop=True), percent_global.reset_index(drop=True)],
                axis=1
            )

            # Versão formatada (##,##%)
            df_percent_global_fmt = df_percent_global.copy()
            for col in fila_cols:
                df_percent_global_fmt[col] = df_percent_global_fmt[col].apply(
                    lambda x: f"{x:.2f}".replace(".", ",") + "%"
                    if pd.notna(x)
                    else ""
                )

            # ==========================
            # 2) ANÁLISE POR HORA (TABELA + GRÁFICO)
            # ==========================

            # Lista de horas disponíveis (todas as que existirem no arquivo)
            horas = sorted(df["Hour"].dropna().unique().tolist())

            st.write(f"**Horas encontradas no arquivo:** {horas}")
            hora_escolhida = st.selectbox("⏰ Selecione uma hora:", horas)

            # Seleciona a linha da hora escolhida
            df_hora = df[df["Hour"] == hora_escolhida]
            if df_hora.empty:
                st.warning("Nenhuma linha encontrada para a hora selecionada.")
            else:
                # Normalmente só 1 linha por hora
                row = df_hora.iloc[0]

                # Converte quantidades das filas para número
                fila_vals = pd.to_numeric(row[fila_cols], errors="coerce")

                # Total da hora (soma de todas as filas)
                total_hora = fila_vals.sum(skipna=True)

                if total_hora is None or np.isclose(total_hora, 0):
                    st.warning("Nenhuma fila com valor maior que zero nessa hora.")
                else:
                    # Calcula percentual de cada fila dentro da hora
                    percentuais = (fila_vals / total_hora) * 100

                    # Mantém apenas filas com percentual > 0
                    mask = percentuais > 0
                    percentuais = percentuais[mask]

                    if percentuais.empty:
                        st.warning("Não há valores percentuais diferentes de zero para essa hora.")
                    else:
                        df_plot = (
                            percentuais
                            .sort_values(ascending=False)
                            .rename_axis("Fila")
                            .reset_index(name="Percentual")
                        )

                        # Formata no padrão brasileiro ##,##%
                        df_plot["Percentual_formatado"] = df_plot["Percentual"].apply(
                            lambda x: f"{x:.2f}".replace(".", ",") + "%"
                        )

                        col1, col2 = st.columns([2, 3])

                        with col1:
                            st.subheader(f"📄 Tabela - Hora {hora_escolhida}")
                            st.dataframe(
                                df_plot[["Fila", "Percentual_formatado"]],
                                use_container_width=True
                            )

                        with col2:
                            st.subheader(f"📈 Gráfico - Hora {hora_escolhida}")
                            st.bar_chart(df_plot.set_index("Fila")["Percentual"])

            # ==========================
            # 3) DOWNLOAD DO RESULTADO GERAL
            # ==========================
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df_percent_global_fmt.to_excel(
                    writer, index=False, sheet_name="Representatividade"
                )
            buffer.seek(0)

            st.download_button(
                label="⬇️ Baixar resultado geral (Excel)",
                data=buffer.getvalue(),
                file_name="Representatividade_por_fila_por_hora.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
else:
    st.info("Envie um arquivo Excel para começar a análise.")
