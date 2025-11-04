# app.py
# Streamlit app para análise de representatividade por fila e hora

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Representatividade por Fila", layout="wide")

st.title("📊 Representatividade por Fila e Hora")
st.write(
    "Envie o arquivo Excel com os dados por fila/hora "
    "(pode ser o arquivo bruto de entrantes ou já em percentual)."
)

uploaded_file = st.file_uploader("📂 Envie o arquivo Excel", type=["xlsx"])

if uploaded_file is not None:
    # Lê o Excel
    df_raw = pd.read_excel(uploaded_file)

    # Garante coluna Hour
    if "Hour" not in df_raw.columns:
        st.error("A coluna 'Hour' não foi encontrada no arquivo.")
    else:
        # Remove coluna Queue se existir (ela é só rótulo)
        if "Queue" in df_raw.columns:
            df = df_raw.drop(columns=["Queue"])
        else:
            df = df_raw.copy()

        st.subheader("📋 Prévia dos Dados")
        st.dataframe(df.head(), use_container_width=True)

        # Identifica colunas de filas (tudo menos Hour e qualquer coluna com 'total')
        total_cols = [c for c in df.columns if "total" in c.lower()]
        cols_excluir = ["Hour"] + total_cols
        fila_cols = [c for c in df.columns if c not in cols_excluir]

        if not fila_cols:
            st.warning("Não foram encontradas colunas de filas (apenas 'Hour' e/ou totais).")
        else:
            # Converte as colunas de filas para número:
            # - remove %, troca vírgula por ponto, remove 'None', 'nan' etc
            df_filas_str = df[fila_cols].astype(str)
            df_filas_str = df_filas_str.replace(
                {
                    "%": "",
                    "None": "",
                    "nan": "",
                    "NaN": "",
                },
                regex=True,
            )
            df_filas_str = df_filas_str.replace(",", ".", regex=True)

            df_filas_num = df_filas_str.apply(pd.to_numeric, errors="coerce")

            # Filtro de hora
            horas = sorted(df["Hour"].dropna().unique().tolist())
            hora_escolhida = st.selectbox("⏰ Selecione uma hora:", horas)

            # Seleciona a linha da hora
            df_hora_num = df_filas_num[df["Hour"] == hora_escolhida]
            if df_hora_num.empty:
                st.warning("Nenhuma linha encontrada para a hora selecionada.")
            else:
                # Normalmente só 1 linha por hora
                row_vals = df_hora_num.iloc[0]

                # Soma total da hora (para calcular percentual)
                total_hora = row_vals.sum(skipna=True)

                if total_hora is None or np.isclose(total_hora, 0):
                    st.warning("Nenhuma fila com valor maior que zero nessa hora.")
                else:
                    # Calcula percentual por fila
                    percentuais = (row_vals / total_hora) * 100

                    # Monta DataFrame para exibição
                    dados = []
                    for fila, valor in percentuais.items():
                        if pd.notna(valor) and not np.isclose(valor, 0):
                            dados.append(
                                {
                                    "Fila": fila,
                                    "Percentual": float(valor),
                                    "Percentual_formatado": f"{valor:.2f}".replace(".", ",") + "%",
                                }
                            )

                    if not dados:
                        st.warning("Não há valores percentuais diferentes de zero para essa hora.")
                    else:
                        df_plot = pd.DataFrame(dados).sort_values("Percentual", ascending=False)

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

        # Botão de download do próprio arquivo enviado (para conveniência)
        st.download_button(
            label="⬇️ Baixar o arquivo enviado",
            data=uploaded_file.getvalue(),
            file_name=uploaded_file.name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
else:
    st.info("Envie um arquivo Excel para começar a análise.")
