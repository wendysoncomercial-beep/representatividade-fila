# app.py
# Streamlit app para análise de representatividade por fila e hora
# + distribuição de agentes com base na representatividade
# + visão macro (todas as horas) e micro (hora selecionada)

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

        # 🔎 Prévia dos dados brutos (como vem do Excel)
        st.subheader("📋 Prévia dos Dados (bruto)")
        st.dataframe(df, use_container_width=True)

        # Identifica colunas de filas (todas menos Hour e qualquer coluna com 'total')
        total_cols = [c for c in df.columns if "total" in c.lower()]
        cols_excluir = ["Hour"] + total_cols
        fila_cols = [c for c in df.columns if c not in cols_excluir]

        if not fila_cols:
            st.warning("Não foram encontradas colunas de filas (apenas 'Hour' e/ou totais).")
        else:
            # ==========================
            # 1) RESULTADO GERAL (TODAS AS HORAS) - MACRO
            # ==========================

            # Converte todas as colunas de filas para número
            df_filas_num_global = df[fila_cols].apply(pd.to_numeric, errors="coerce")

            # Total por hora (linha)
            total_hora_global = df_filas_num_global.sum(axis=1)

            # Percentual por fila em cada hora (numérico)
            percent_global = df_filas_num_global.div(
                total_hora_global.replace(0, np.nan), axis=0
            ) * 100

            # DataFrame geral com Hour + filas (numérico)
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

            # 👉 VISÃO GERAL (MACRO) - REPRESENTATIVIDADE
            st.subheader("🌎 Visão Geral (Macro) - Representatividade por Hora")
            st.write(
                "Cada linha representa uma hora, e cada coluna de fila traz a participação "
                "percentual daquela fila dentro da hora."
            )
            st.dataframe(df_percent_global_fmt, use_container_width=True)

            # ==========================
            # 1.1) DISTRIBUIÇÃO GERAL DE AGENTES (TODAS AS HORAS)
            # ==========================

            st.subheader("👥 Visão Geral - Distribuição de Agentes (todas as horas)")
            total_agentes_global = st.number_input(
                "Informe o total de agentes disponíveis por hora (mesmo valor para todas as horas):",
                min_value=0,
                step=1,
                value=0,
            )

            df_agentes_global_long = None

            if total_agentes_global > 0:
                # Percentuais em formato numérico, trocando NaN por 0
                perc = percent_global.fillna(0)

                # Raw = agentes fracionários
                raw = perc * total_agentes_global / 100.0

                # Parte inteira
                base = np.floor(raw).astype(int)

                # Ajuste por linha (hora) para garantir que a soma = total_agentes_global
                agentes_ajustados = base.copy()
                for i in range(agentes_ajustados.shape[0]):
                    soma_linha = agentes_ajustados.iloc[i].sum()
                    sobra = int(total_agentes_global - soma_linha)
                    if sobra > 0:
                        # distribui sobrando pros maiores decimais daquela hora
                        frac = (raw.iloc[i] - base.iloc[i]).sort_values(ascending=False)
                        idx_extra = frac.index[:sobra]
                        agentes_ajustados.loc[i, idx_extra] += 1

                # Cria tabela larga: Hour x Fila (Agentes)
                df_agentes_wide = pd.concat(
                    [df["Hour"].reset_index(drop=True), agentes_ajustados.reset_index(drop=True)],
                    axis=1
                )

                # Cria tabela longa: Hour, Fila, Percentual, Agentes
                registros = []
                for i, hora in enumerate(df["Hour"].tolist()):
                    for fila in fila_cols:
                        agentes = int(agentes_ajustados.iloc[i][fila])
                        percentual = float(perc.iloc[i][fila])
                        if agentes > 0 and percentual > 0:
                            registros.append(
                                {
                                    "Hour": hora,
                                    "Fila": fila,
                                    "Percentual": percentual,
                                    "Percentual_formatado": f"{percentual:.2f}".replace(".", ",") + "%",
                                    "Agentes_sugeridos": agentes,
                                }
                            )

                if registros:
                    df_agentes_global_long = pd.DataFrame(registros)

                    st.markdown("**Tabela larga (Hour x Fila com agentes):**")
                    st.dataframe(df_agentes_wide, use_container_width=True)

                    st.markdown("**Tabela detalhada (Hour, Fila, %, Agentes):**")
                    st.dataframe(df_agentes_global_long, use_container_width=True)

                    # Download da distribuição geral de agentes (tabela longa)
                    buf_agents_global = io.BytesIO()
                    with pd.ExcelWriter(buf_agents_global, engine="openpyxl") as writer:
                        df_agentes_wide.to_excel(
                            writer,
                            index=False,
                            sheet_name="Distribuicao_Agentes_Wide",
                        )
                        df_agentes_global_long.to_excel(
                            writer,
                            index=False,
                            sheet_name="Distribuicao_Agentes_Long",
                        )
                    buf_agents_global.seek(0)

                    st.download_button(
                        label="⬇️ Baixar distribuição geral de agentes (Excel)",
                        data=buf_agents_global.getvalue(),
                        file_name="Distribuicao_agentes_geral.xlsx",
                        mime=(
                            "application/vnd.openxmlformats-officedocument."
                            "spreadsheetml.sheet"
                        ),
                    )
                else:
                    st.info(
                        "Não foi possível calcular a distribuição geral de agentes — "
                        "verifique se há volume em alguma hora."
                    )

            # ==========================
            # 2) ANÁLISE POR HORA (MICRO) - DETALHE
            # ==========================

            st.subheader("🔍 Visão por Hora (Micro)")

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
                        # 2.1) DISTRIBUIÇÃO DE AGENTES (MICRO)
                        # ==========================

                        st.subheader(f"👥 Distribuição de agentes - Hora {hora_escolhida}")
                        total_agentes = st.number_input(
                            "Informe o total de agentes disponíveis nessa hora:",
                            min_value=0,
                            step=1,
                            value=0,
                            key="input_agentes_hora",
                        )

                        if total_agentes > 0:
                            # Cálculo proporcional: agentes = total * percentual / 100
                            raw = total_agentes * df_plot["Percentual"] / 100.0

                            # Parte inteira
                            base = np.floor(raw).astype(int)
                            df_agentes = df_plot.copy()
                            df_agentes["Agentes_sugeridos"] = base

                            # Ajuste para garantir que a soma = total_agentes
                            sobra = int(total_agentes - base.sum())
                            if sobra > 0:
                                frac = (raw - base).sort_values(ascending=False)
                                idx_extra = frac.index[:sobra]
                                df_agentes.loc[idx_extra, "Agentes_sugeridos"] += 1

                            st.dataframe(
                                df_agentes[["Fila", "Percentual_formatado", "Agentes_sugeridos"]],
                                use_container_width=True
                            )

                            # Botão de download da distribuição de agentes dessa hora
                            buf_agents = io.BytesIO()
                            with pd.ExcelWriter(buf_agents, engine="openpyxl") as writer:
                                df_agentes.to_excel(
                                    writer,
                                    index=False,
                                    sheet_name=f"Distribuicao_H{hora_escolhida}"
                                )
                            buf_agents.seek(0)

                            st.download_button(
                                label="⬇️ Baixar distribuição de agentes dessa hora (Excel)",
                                data=buf_agents.getvalue(),
                                file_name=f"Distribuicao_agentes_hora_{hora_escolhida}.xlsx",
                                mime=(
                                    "application/vnd.openxmlformats-officedocument."
                                    "spreadsheetml.sheet"
                                ),
                            )

            # ==========================
            # 3) DOWNLOAD DO RESULTADO GERAL (MACRO)
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
