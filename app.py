# app.py
# Streamlit app para análise de representatividade por fila e hora

import streamlit as st
import pandas as pd
import numpy as np

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

        st.subheader("📋 Prévia dos Dados")
        st.dataframe(df.head(), use_container_width=True)

        # Identifica colunas de filas (todas menos Hour e qualquer coluna com 'total')
        total_cols = [c for c in df.columns if "total" in c.lower()]
        cols_excluir = ["Hour"] + total_cols
        fila_cols = [c for c in df.columns if c not in cols_excluir]

        if not fila_cols:
            st.warning("Não foram encontradas colunas de filas (apenas 'Hour' e/ou totais).")
        else:
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

        # Botão de download do próprio arquivo enviado
        st.download_button(
            label="⬇️ Baixar o arquivo enviado",
            data=uploaded_file.getvalue(),
            file_name=uploaded_file.name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
else:
    st.info("Envie um arquivo Excel para começar a análise.")
