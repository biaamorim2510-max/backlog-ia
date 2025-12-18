import datetime
import random

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

# =========================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================
st.set_page_config(page_title="Backlog de Iniciativas com IA", page_icon="🤖", layout="wide")

st.title("Backlog de iniciativas com IA")
st.write(
    """
    Espaço único para registrar e acompanhar **ideias, automações e iniciativas com IA**.

    **Como usar:**
    - Registre uma iniciativa.
    - Toda iniciativa nasce com **Status = Nova**.
    - Atualize **Status** e **Responsável** direto na tabela.
    """
)

# =========================================
# DADOS INICIAIS (EXEMPLO) - SESSION STATE
# =========================================
if "df" not in st.session_state:
    np.random.seed(42)

    iniciativas_fake = [
        "Automatizar triagem de demandas com IA",
        "Gerar resumo automático de reuniões e Status Report",
        "Classificar atritos 2R/4R com IA para direcionamento",
        "Painel de ROI das iniciativas de IA (horas economizadas)",
        "Assistente para padronizar cadastro e follow-up no CRM",
        "Chat interno de dúvidas sobre processos (base de conhecimento)",
        "Automação de captura e anexos de documentos em workflow",
        "Detecção de duplicidade de leads e melhoria de qualidade de dados",
        "Sugestão de respostas para atendimento (WhatsApp/CRM)",
        "Comparador de produtos/modelos com argumentos de venda",
    ]

    data = {
        "ID": [f"INI-{i}" for i in range(1100, 1000, -1)],
        "Iniciativa": np.random.choice(iniciativas_fake, size=100),
        "Status": np.random.choice(
            ["Nova", "Priorizada", "Em execução", "Pausada", "Concluída"], size=100
        ),
        "Tipo": np.random.choice(["Ideia", "IA", "Automação", "Melhoria de processo"], size=100),
        "Responsável": np.random.choice(["", "Inovação", "TI", "Operações", "Comercial"], size=100),
        "Data de registro": [
            datetime.date(2025, 1, 1) + datetime.timedelta(days=random.randint(0, 330))
            for _ in range(100)
        ],
    }
    st.session_state.df = pd.DataFrame(data)

df = st.session_state.df

st.divider()

# =========================================
# CADASTRO DE NOVA INICIATIVA
# =========================================
st.header("➕ Registrar nova iniciativa")

with st.form("add_initiative_form"):
    c1, c2, c3 = st.columns([2, 1, 1])

    iniciativa = c1.text_area("Descreva a ideia ou problema (obrigatório)")
    tipo = c2.selectbox("Tipo de iniciativa", ["Ideia", "IA", "Automação", "Melhoria de processo"])
    area = c3.selectbox("Área (opcional)", ["", "Comercial", "RH", "Financeiro", "Operações", "TI", "Outros"])

    submitted = st.form_submit_button("Salvar")

if submitted:
    if not iniciativa.strip():
        st.error("Preencha a descrição da iniciativa antes de salvar.")
    else:
        # Gera novo ID incremental com base no maior existente (INI-xxxx)
        recent_number = int(max(st.session_state.df["ID"]).split("-")[1])
        today = datetime.date.today()

        df_new = pd.DataFrame(
            [
                {
                    "ID": f"INI-{recent_number+1}",
                    "Iniciativa": iniciativa.strip(),
                    "Status": "Nova",
                    "Tipo": tipo,
                    "Responsável": "",
                    "Data de registro": today,
                    "Área": area,
                }
            ]
        )

        # Se a coluna Área não existir no dataset antigo, cria
        if "Área" not in st.session_state.df.columns:
            st.session_state.df["Área"] = ""

        st.session_state.df = pd.concat([df_new, st.session_state.df], axis=0, ignore_index=True)

        st.success("Iniciativa registrada! ✅")
        st.dataframe(df_new, use_container_width=True, hide_index=True)

st.divider()

# =========================================
# VISUALIZAÇÃO + EDIÇÃO DO BACKLOG
# =========================================
st.header("📌 Iniciativas registradas")

# Garantir coluna "Área" (caso dataset inicial não tenha)
if "Área" not in st.session_state.df.columns:
    st.session_state.df["Área"] = ""

f1, f2, f3, f4 = st.columns([1, 1, 1, 2])

f_status = f1.selectbox("Filtrar por Status", ["Todos", "Nova", "Priorizada", "Em execução", "Pausada", "Concluída"])
f_tipo = f2.selectbox("Filtrar por Tipo", ["Todos", "Ideia", "IA", "Automação", "Melhoria de processo"])
f_area = f3.selectbox("Filtrar por Área", ["Todos", "", "Comercial", "RH", "Financeiro", "Operações", "TI", "Outros"])
busca = f4.text_input("Buscar (por texto na iniciativa)")

vis = st.session_state.df.copy()

if f_status != "Todos":
    vis = vis[vis["Status"] == f_status]
if f_tipo != "Todos":
    vis = vis[vis["Tipo"] == f_tipo]
if f_area != "Todos":
    vis = vis[vis["Área"] == f_area]
if busca.strip():
    vis = vis[vis["Iniciativa"].str.contains(busca, case=False, na=False)]

st.write(f"Total de iniciativas: `{len(st.session_state.df)}` | Mostrando: `{len(vis)}`")

st.info(
    "Dica: atualize **Status** e **Responsável** direto na tabela (duplo clique).",
    icon="✍️",
)

edited_df = st.data_editor(
    vis,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Status": st.column_config.SelectboxColumn(
            "Status",
            help="Etapa atual da iniciativa",
            options=["Nova", "Priorizada", "Em execução", "Pausada", "Concluída"],
            required=True,
        ),
        "Tipo": st.column_config.SelectboxColumn(
            "Tipo",
            help="Classificação da iniciativa",
            options=["Ideia", "IA", "Automação", "Melhoria de processo"],
            required=True,
        ),
        "Área": st.column_config.SelectboxColumn(
            "Área",
            help="Área relacionada (opcional)",
            options=["", "Comercial", "RH", "Financeiro", "Operações", "TI", "Outros"],
            required=False,
        ),
        "Responsável": st.column_config.TextColumn(
            "Responsável",
            help="Quem está tocando (nome ou time)",
        ),
        "Data de registro": st.column_config.DateColumn(
            "Data de registro",
            help="Data em que a iniciativa foi registrada",
            format="DD/MM/YYYY",
        ),
    },
    disabled=["ID"],
)

# =========================================
# SINCRONIZAR EDIÇÕES DE VOLTA PARA O DATASET PRINCIPAL
# (para não perder alterações após filtro/busca)
# =========================================
# Estratégia: atualiza o dataframe principal por ID
df_main = st.session_state.df.copy()

# Usa o ID como chave para atualizar linhas editadas
edited_df_indexed = edited_df.set_index("ID")
df_main_indexed = df_main.set_index("ID")

for col in ["Iniciativa", "Status", "Tipo", "Responsável", "Área", "Data de registro"]:
    if col in edited_df_indexed.columns and col in df_main_indexed.columns:
        df_main_indexed.loc[edited_df_indexed.index, col] = edited_df_indexed[col]

st.session_state.df = df_main_indexed.reset_index()

st.divider()

# =========================================
# INDICADORES
# =========================================
st.header("📊 Indicadores do backlog")

col1, col2, col3, col4 = st.columns(4)
num_novas = len(st.session_state.df[st.session_state.df["Status"] == "Nova"])
num_prio = len(st.session_state.df[st.session_state.df["Status"] == "Priorizada"])
num_exec = len(st.session_state.df[st.session_state.df["Status"] == "Em execução"])
num_conc = len(st.session_state.df[st.session_state.df["Status"] == "Concluída"])

col1.metric("Novas", num_novas)
col2.metric("Priorizadas", num_prio)
col3.metric("Em execução", num_exec)
col4.metric("Concluídas", num_conc)

st.write("")

# =========================================
# GRÁFICOS
# =========================================
st.subheader("Status por mês (base: Data de registro)")

status_plot = (
    alt.Chart(st.session_state.df)
    .mark_bar()
    .encode(
        x="month(Data de registro):O",
        y="count():Q",
        xOffset="Status:N",
        color="Status:N",
        tooltip=["Status:N", "count():Q"],
    )
    .configure_legend(orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5)
)
st.altair_chart(status_plot, use_container_width=True, theme="streamlit")

st.subheader("Distribuição por tipo de iniciativa")

tipo_plot = (
    alt.Chart(st.session_state.df)
    .mark_arc()
    .encode(theta="count():Q", color="Tipo:N", tooltip=["Tipo:N", "count():Q"])
    .properties(height=300)
    .configure_legend(orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5)
)
st.altair_chart(tipo_plot, use_container_width=True, theme="streamlit")

st.caption("Observação: este app usa dados de exemplo e persiste apenas durante a sessão/estado atual do app.")
