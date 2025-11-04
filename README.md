# 📊 Representatividade por Fila e Hora (Streamlit)

Este repositório contém um app em **Streamlit** para analisar a representatividade (%) de cada fila por hora,
com base em um arquivo Excel gerado previamente (ex.: `Representatividade_por_fila_por_hora.xlsx`).

## 🚀 Funcionalidades

- Upload de arquivo Excel com colunas:
  - `Hour` (hora, ex.: 0, 1, 2, ..., 23)
  - Uma coluna opcional de total por hora (ex.: `Total_Hora`)
  - Demais colunas representando filas, com valores em percentual (ex.: `12,34%` ou `12.34%`)
- Seleção da **hora** para análise
- Visualização em:
  - Tabela com fila x percentual
  - Gráfico de barras das filas com maior representatividade
- Botão para baixar novamente o arquivo enviado

## 📂 Estrutura de Arquivos

```text
.
├── app.py              # Código principal do app Streamlit
├── requirements.txt    # Dependências do projeto
└── README.md           # Este arquivo
```

## 🧩 Como rodar localmente

1. Clone o repositório ou faça download dos arquivos:
   ```bash
   git clone https://github.com/<seu-usuario>/<seu-repositorio>.git
   cd <seu-repositorio>
   ```

2. Crie um ambiente virtual (opcional, mas recomendado):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate   # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Rode o app Streamlit:
   ```bash
   streamlit run app.py
   ```

5. Abra o navegador no endereço indicado (geralmente `http://localhost:8501`).

## 📥 Formato esperado do arquivo Excel

- A primeira coluna deve ser `Hour` (inteiro representando a hora do dia).
- As demais colunas devem ser:
  - Uma coluna opcional de total da hora (ex.: `Total_Hora`)
  - Colunas de filas com valores percentuais, em qualquer um dos formatos:
    - `12,34%`
    - `12.34%`
    - `12.34`

Exemplo simplificado:

| Hour | Fila A   | Fila B   | Fila C   | Total_Hora |
|------|----------|----------|----------|------------|
| 8    | 50,00%   | 30,00%   | 20,00%   | 100        |
| 9    | 40,00%   | 40,00%   | 20,00%   | 80         |

## 🌐 Publicando no Streamlit Cloud

1. Suba estes arquivos para um repositório no GitHub.
2. Acesse [https://share.streamlit.io](https://share.streamlit.io).
3. Conecte sua conta do GitHub e selecione o repositório.
4. Informe o caminho do arquivo principal: `app.py`.
5. O Streamlit Cloud instalará as dependências a partir do `requirements.txt` e subirá o app automaticamente.

---

Qualquer ajuste fino (layout, filtros adicionais, outros gráficos) pode ser feito diretamente no `app.py`.
