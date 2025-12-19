import datetime

import altair as alt
import pandas as pd
import streamlit as st

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Backlog de Iniciativas com IA", page_icon="🤖", layout="wide")

st.title("Backlog de iniciativas com IA")
st.write(
    """
    Cadastro e acompanhamento de iniciativas com IA.

    **Regras simples**
    - Cada iniciativa nasce com **Status = A iniciar**
    - Atualize **Status**, **Ganhos obtidos** e **Comentário** ao longo da execução
    """
)

# =========================
# LISTAS (OPÇÕES)
# =========================
STATUS_OPCOES = ["A iniciar", "Em andamento", "Em produção", "Em homologação", "Descartada"]
FREQUENCIA_OPCOES = ["Diária", "Semanal", "Mensal", "Anual"]

SETORES_OPCOES = [
    "Inovação", "TI", "Operações", "Comercial", "RH", "Financeiro", "Marketing", "Pós-venda", "Outros"
]
CATEGORIAS_OPCOES = [
    "Ideia", "IA", "Automação", "Melhoria de processo", "Dados/BI", "Atendimento/CRM", "Compliance", "Outros"
]
INDICADORES_OPCOES = [
    "Tempo de execução", "Custo operacional", "Produtividade", "Qualidade do dado", "SLA", "Conversão",
    "Receita", "Satisfação do cliente", "Erro operacional", "Outro"
]

# =========================
# ESTRUTURA (COLUNAS)
# =========================
COLS = [
    "ID",
    "Data de inclusão",
    "Setor responsável",
    "Categoria de iniciativa",
    "Título da Iniciativa",
    "Dor tratada",
    "Solução proposta",
    "Status",
    "Ganhos obtidos",
    "Comentário",
    "Indicador-chave afetado",
    "Valor antes da IA",
    "Valor estimado após IA",
    "Valor real após IA",
    "Frequência",
]

# =========================
# SESSION STATE (SEM DADOS FAKE)
# =========================
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=COLS)

# =========================
# CADASTRO
# =========================
st.divider()
st.header("➕ Registrar nova iniciativa")

with st.form("form_cadastro"):
    c1, c2, c3 = st.columns([1.1, 1.1, 1.1])
    setor = c1.selectbox("Setor responsável", SETORES_OPCOES)
    categoria = c2.selectbox("Categoria de iniciativa", CATEGORIAS_OPCOES)
    status = c3.selectbox("Status", STATUS_OPCOES, index=0)

    titulo = st.text_input("Título da Iniciativa (obrigatório)")

    c4, c5 = st.columns([1, 1])
    dor = c4.text_area("Dor tratada", height=110)
    solucao = c5.text_area("Solução proposta", height=110)

    c6, c7 = st.columns([1.2, 1.2])
    indicador = c6.selectbox("Indicador-chave afetado", INDICADORES_OPCOES)
    frequencia = c7.selectbox("Frequência", FREQUENCIA_OPCOES)

    c9, c10, c11 = st.columns(3)
    v_antes = c9.text_input("Valor antes da IA (ex.: 1h, 30m, 6 meses)")
    v_estimado = c10.text_input("Valor estimado após IA (ex.: 20m, 4 meses)")
    v_real = c11.text_input("Valor real após IA (ex.: 15m, 3 meses)")

    c12, c13 = st.columns(2)
    ganhos = c12.text_area("Ganhos obtidos", height=110)
    comentario = c13.text_area("Comentário", height=110)

    salvar = st.form_submit_button("Salvar iniciativa")

if salvar:
    if not titulo.strip():
        st.error("Preencha o **Título da Iniciativa** para salvar.")
    else:
        df = st.session_state.df.copy()

        # Novo ID incremental (INI-1, INI-2, ...)
        if df.empty:
            new_id = "INI-1"
        else:
            # Garantia: pega apenas os IDs no padrão INI-<numero>
            ids = df["ID"].astype(str).tolist()
            nums = []
            for x in ids:
                try:
                    nums.append(int(str(x).split("-")[1]))
                except Exception:
                    pass
            new_id = f"INI-{(max(nums) + 1) if nums else 1}"

        df_new = pd.DataFrame(
            [
                {
                    "ID": new_id,
                    "Data de inclusão": datetime.date.today(),
                    "Setor responsável": setor,
                    "Categoria de iniciativa": categoria,
                    "Título da Iniciativa": titulo.strip(),
                    "Dor tratada": dor.strip(),
                    "Solução proposta": solucao.strip(),
                    "Status": status,
                    "Ganhos obtidos": ganhos.strip(),
                    "Comentário": comentario.strip(),
                    "Indicador-chave afetado": indicador,
                    "Valor antes da IA": v_antes.strip(),
                    "Valor estimado após IA": v_estimado.strip(),
                    "Valor real após IA": v_real.strip(),
                    "Frequência": frequencia,
                }
            ],
            columns=COLS,
        )

        st.session_state.df = pd.concat([df_new, df], axis=0, ignore_index=True)
        st.success(f"Iniciativa registrada ✅ (ID: {new_id})")
        st.dataframe(df_new, use_container_width=True, hide_index=True)

# =========================
# BACKLOG (CONSULTA + EDIÇÃO)
# =========================
st.divider()
st.header("📌 Backlog (consulta e atualização)")

df_main = st.session_state.df.copy()

# Normaliza a coluna de data para evitar erro de tipo no data_editor
if not df_main.empty:
    df_main["Data de inclusão"] = pd.to_datetime(df_main["Data de inclusão"], errors="coerce").dt.date
    df_main["Data de inclusão"] = df_main["Data de inclusão"].fillna(datetime.date.today())

f1, f2, f3, f4 = st.columns([1, 1, 1, 2])
flt_status = f1.selectbox("Filtrar Status", ["Todos"] + STATUS_OPCOES)
flt_setor = f2.selectbox("Filtrar Setor", ["Todos"] + SETORES_OPCOES)
flt_cat = f3.selectbox("Filtrar Categoria", ["Todos"] + CATEGORIAS_OPCOES)
busca = f4.text_input("Buscar (título / dor / solução)")

vis = df_main.copy()

if flt_status != "Todos":
    vis = vis[vis["Status"] == flt_status]
if flt_setor != "Todos":
    vis = vis[vis["Setor responsável"] == flt_setor]
if flt_cat != "Todos":
    vis = vis[vis["Categoria de iniciativa"] == flt_cat]
if busca.strip() and not vis.empty:
    mask = (
        vis["Título da Iniciativa"].astype(str).str.contains(busca, case=False, na=False)
        | vis["Dor tratada"].astype(str).str.contains(busca, case=False, na=False)
        | vis["Solução proposta"].astype(str).str.contains(busca, case=False, na=False)
    )
    vis = vis[mask]

st.write(f"Total no backlog: `{len(df_main)}` | Mostrando: `{len(vis)}`")

if df_main.empty:
    st.warning("Ainda não há iniciativas cadastradas. Use o formulário acima para criar a primeira.")
else:
    st.info(
        "Você pode editar a tabela (duplo clique). Sugestão: mantenha **Status**, **Ganhos obtidos** e **Comentário** sempre atualizados.",
        icon="✍️",
    )

    edited = st.data_editor(
        vis,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Data de inclusão": st.column_config.DateColumn("Data de inclusão", format="DD/MM/YYYY"),
            "Setor responsável": st.column_config.SelectboxColumn("Setor responsável", options=SETORES_OPCOES, required=True),
            "Categoria de iniciativa": st.column_config.SelectboxColumn("Categoria de iniciativa", options=CATEGORIAS_OPCOES, required=True),
            "Status": st.column_config.SelectboxColumn("Status", options=STATUS_OPCOES, required=True),
            "Indicador-chave afetado": st.column_config.SelectboxColumn("Indicador-chave afetado", options=INDICADORES_OPCOES, required=True),
            "Frequência": st.column_config.SelectboxColumn("Frequência", options=FREQUENCIA_OPCOES, required=True),
            "Valor antes da IA": st.column_config.TextColumn("Valor antes da IA"),
            "Valor estimado após IA": st.column_config.TextColumn("Valor estimado após IA"),
            "Valor real após IA": st.column_config.TextColumn("Valor real após IA"),
            "Ganhos obtidos": st.column_config.TextColumn("Ganhos obtidos"),
            "Comentário": st.column_config.TextColumn("Comentário"),
        },
        disabled=["ID"],
    )

    # =========================
    # SINCRONIZAÇÃO DAS EDIÇÕES
    # =========================
    df_main_idx = df_main.set_index("ID")
    edited_idx = edited.set_index("ID")

    cols_to_update = [c for c in edited_idx.columns if c in df_main_idx.columns]
    for col in cols_to_update:
        df_main_idx.loc[edited_idx.index, col] = edited_idx[col]

    st.session_state.df = df_main_idx.reset_index()

    # Re-normaliza após edição (Streamlit pode voltar como Timestamp/string)
    st.session_state.df["Data de inclusão"] = pd.to_datetime(
        st.session_state.df["Data de inclusão"], errors="coerce"
    ).dt.date
    st.session_state.df["Data de inclusão"] = st.session_state.df["Data de inclusão"].fillna(datetime.date.today())

# =========================
# INDICADORES + GRÁFICOS
# =========================
st.divider()
st.header("📊 Indicadores")

df_kpi = st.session_state.df.copy()

if df_kpi.empty:
    st.info("Quando você cadastrar iniciativas, os indicadores e gráficos aparecerão aqui.")
else:
    df_kpi["Data de inclusão"] = pd.to_datetime(df_kpi["Data de inclusão"], errors="coerce").dt.date
    df_kpi["Data de inclusão"] = df_kpi["Data de inclusão"].fillna(datetime.date.today())

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("A iniciar", int((df_kpi["Status"] == "A iniciar").sum()))
    c2.metric("Em andamento", int((df_kpi["Status"] == "Em andamento").sum()))
    c3.metric("Em produção", int((df_kpi["Status"] == "Em produção").sum()))
    c4.metric("Em homologação", int((df_kpi["Status"] == "Em homologação").sum()))
    c5.metric("Descartadas", int((df_kpi["Status"] == "Descartada").sum()))

    st.write("")
    st.subheader("Status por mês (Data de inclusão)")
    status_plot = (
        alt.Chart(df_kpi)
        .mark_bar()
        .encode(
            x="yearmonth(Data de inclusão):O",
            y="count():Q",
            xOffset="Status:N",
            color="Status:N",
            tooltip=["Status:N", "count():Q"],
        )
        .configure_legend(orient="bottom")
    )
    st.altair_chart(status_plot, use_container_width=True, theme="streamlit")

    st.subheader("Distribuição por Categoria de iniciativa")
    cat_plot = (
        alt.Chart(df_kpi)
        .mark_bar()
        .encode(
            x=alt.X("Categoria de iniciativa:N", sort="-y"),
            y="count():Q",
            tooltip=["Categoria de iniciativa:N", "count():Q"],
        )
    )
    st.altair_chart(cat_plot, use_container_width=True, theme="streamlit")

st.caption(
    "Observação: este protótipo usa session_state. Se o app reiniciar, pode perder dados. "
    "Próximo passo recomendado: persistir em arquivo/banco e aplicar controle de acesso."
)

