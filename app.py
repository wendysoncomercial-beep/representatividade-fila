# app.py
# Streamlit app para análise de representatividade por fila e hora

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Representatividade por Fila", layout="wide")

st.title("📊 Representatividade por Fila e Hora")
st.write(
    "Envie o arquivo Excel com a representatividade por fila/hora "
    "(ex.: `Representatividade_por_fila_por_hora.xlsx`)."
)

uploaded_file = st.file_uploader("📂 Envie o arquivo Excel", type=["xlsx"])

if uploaded_file is not None:
    # Lê o Excel
    df = pd.read_excel(uploaded_file)

    # Garante nomes de colunas esperadas
    if "Hour" not in df.columns:
        st.error("A coluna 'Hour' não foi encontrada no arquivo.")
    else:
        # Descobre coluna de total da hora (se existir)
        total_cols = [c for c in df.columns if "total" in c.lower()]
        total_col = total_cols[0] if total_cols else None

        st.subheader("📋 Prévia dos Dados")
        st.dataframe(df.head(), use_container_width=True)

        # Colunas de percentual:
        # se tiver coluna de total, exclui Hour + total; se não tiver, exclui só Hour
        if total_col:
            percent_cols = [c for c in df.columns if c not in ["Hour", total_col]]
        else:
            percent_cols = [c for c in df.columns if c != "Hour"]

        # Filtro de hora
        horas = sorted(df["Hour"].dropna().unique().tolist())
        hora_escolhida = st.selectbox("⏰ Selecione a hora:", horas)

        # Filtra linha da hora escolhida
        df_hora = df[df["Hour"] == hora_escolhida].copy()
        if df_hora.empty:
            st.warning("Nenhuma linha encontrada para a hora selecionada.")
        else:
            # Normalmente haverá 1 linha por hora; pegamos a primeira
            row = df_hora.iloc[0].copy()

            # Monta DataFrame no formato (Fila, Percentual)
            dados = []
            for col in percent_cols:
                val = row[col]

                # Tenta converter string "12,34%" ou "12.34%" em número
                if isinstance(val, str):
                    val_str = val.strip().replace("%", "").replace(",", ".")
                    try:
                        num = float(val_str)
                    except ValueError:
                        num = None
                else:
                    num = float(val) if pd.notna(val) else None

                if num is not None and not pd.isna(num) and num != 0:
                    dados.append({"Fila": col, "Percentual": num})

            if not dados:
                st.warning("Não há valores de percentual diferentes de zero para essa hora.")
            else:
                df_plot = pd.DataFrame(dados).sort_values("Percentual", ascending=False)

                # 👉 Aqui formatamos o percentual no padrão brasileiro ##,##%
                df_plot["Percentual_formatado"] = df_plot["Percentual"].apply(
                    lambda x: f"{x:.2f}".replace(".", ",") + "%"
                )

                col1, col2 = st.columns([2, 3])

                with col1:
                    st.subheader(f"📄 Tabela - Hora {hora_escolhida}")
                    # Mostra só Fila + Percentual formatado
                    st.dataframe(
                        df_plot[["Fila", "Percentual_formatado"]],
                        use_container_width=True
                    )

                with col2:
                    st.subheader(f"📈 Gráfico - Hora {hora_escolhida}")
                    # Gráfico usa o valor numérico (com ponto)
                    st.bar_chart(
                        df_plot.set_index("Fila")["Percentual"]
                    )

        # Botão de download do próprio arquivo enviado (para conveniência)
        st.download_button(
            label="⬇️ Baixar o arquivo enviado",
            data=uploaded_file.getvalue(),
            file_name=uploaded_file.name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
else:
    st.info("Envie um arquivo Excel para começar a análise.")
