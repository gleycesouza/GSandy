import streamlit as st
import previsao_modelo
import base64
import pandas as pd
import plotly.express as px
import numpy as np

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GSandy",
    page_icon="./logo_gsandy.png",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background-color: #FFFFFF; }
  [data-testid="stHeader"]           { background-color: transparent; }
  section[data-testid="stSidebar"]   { display: none; }

  html, body, [class*="css"] {
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
  }

  h1 { font-size: 1.75rem !important; font-weight: 700; color: #111; letter-spacing: 0.01em; }
  h3 { font-size: 1.0rem  !important; font-weight: 600; color: #222; margin-bottom: 0.15rem; }

  hr { border-color: #EFEFEF !important; }

  .stCaption p { color: #666 !important; font-size: 0.85rem !important; }

  /* Button */
  .stButton > button {
    background-color: #1C1C1C !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 0.55rem 1.5rem !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    width: 100% !important;
    letter-spacing: 0.02em !important;
    transition: background-color 0.15s ease !important;
  }
  .stButton > button:hover { background-color: #383838 !important; }

  /* Expanders */
  [data-testid="stExpander"] {
    border: 1px solid #EBEBEB !important;
    border-radius: 6px !important;
    background: #FDFDFD !important;
  }

  /* Tabs */
  [data-testid="stTabs"] [data-baseweb="tab"] { font-size: 0.86rem; }

  /* Radio (language toggle) */
  div[data-testid="stHorizontalBlock"] label { font-size: 0.85rem; }

  /* Responsive */
  @media (max-width: 640px) {
    h1 { font-size: 1.3rem !important; }
    .stButton > button { font-size: 0.85rem !important; padding: 0.5rem 1rem !important; }
  }
</style>
""", unsafe_allow_html=True)

# ── Bilingual content ──────────────────────────────────────────────────────────
TEXTS = {
    "PT": {
        "subtitle": "Simulador de ensaios de cisalhamento em areias",
        "about_title": "Sobre o GSandy",
        "about_body": (
            "O **GSandy** é uma ferramenta acadêmica desenvolvida como parte de dissertação de mestrado "
            "em Geotecnia pela PUC-Rio. O programa utiliza dados de ensaios de cisalhamento direto e DSS "
            "da literatura científica para simular a relação tensão × deformação/deslocamento em areias.\n\n"
            "Os modelos empregados — **Random Forest**, **SVR** e **FNN** — foram treinados exclusivamente "
            "com dados de areia e validados em contexto acadêmico.\n\n"
            "Para detalhes sobre a metodologia, consulte a dissertação "
            "*\"Machine Learning para Previsão do Comportamento de Areias em Ensaios de Cisalhamento "
            "Direto e DSS\"* (Baptista, 2024)."
        ),
        "sim_title": "Configuração da Simulação",
        "test_label": "Tipo de ensaio",
        "test_opts": ["DSS", "Cisalhamento Direto"],
        "gs_label": "$G_s$ — Densidade real dos grãos",
        "e0_label": "$e_0$ — Índice de vazios inicial",
        "cr_label": "$CR$ — Compacidade Relativa (%)",
        "sv_label": "$\\sigma_v$ — Tensão Vertical (kPa)",
        "btn": "Simular",
        "spinner": "Calculando previsões...",
        "success": "Simulação concluída.",
        "tab_chart": "Gráfico",
        "tab_data": "Dados",
        "tab_metrics": "Métricas",
        "tab_val": "Validação",
        "tab_src": "Fontes",
        "chart_title": "Previsão τ/σ",
        "model_col": "Modelo",
        "model_names": ["Random Forest", "SVR", "Rede Neural"],
        "metrics_cap": "Métricas de desempenho — Treinamento e Teste",
        "metrics_expand": "O que significam essas métricas?",
        "metrics_help": (
            "**R²** (coeficiente de determinação): mede o quanto o modelo explica a variabilidade dos dados. "
            "Varia de 0 a 1; quanto mais próximo de 1, melhor o ajuste.\n\n"
            "**RMSE** (raiz do erro quadrático médio): está na mesma unidade da variável alvo e penaliza "
            "erros grandes — valores menores indicam melhor desempenho.\n\n"
            "**MAE** (erro absoluto médio): média dos desvios absolutos entre previsão e valor real; "
            "representa o erro típico na escala original da variável."
        ),
        "val_cap": "Resultados dos modelos nos ensaios de validação",
        "val_help": (
            "Comparação entre os valores previstos e os valores experimentais nos ensaios de validação "
            "(dados não utilizados no treinamento)."
        ),
        "src_cap": "Base de dados utilizada no treinamento dos modelos",
        "refs_exp": "Referências Bibliográficas",
        "recog_title": "Reconhecimentos e Publicações",
        "recog_intro": (
            "O GSandy e a dissertação associada foram reconhecidos nas seguintes "
            "publicações e eventos científicos:"
        ),
        "tag_award": "PRÊMIO",
        "tag_conf": "CONGRESSO",
        "tag_article": "ARTIGO",
        "tag_thesis": "DISSERTAÇÃO",
        "tag_pdf": "PDF",
        "tag_reg": "REGISTRO",
        "cite_title": "Como Citar este Trabalho",
        "cite_intro": (
            "Caso utilize o GSandy ou a dissertação associada em seu trabalho, "
            "por favor cite as referências abaixo:"
        ),
        "cite_sw_label": "Software",
        "cite_diss_label": "Dissertação",
        "cite_sw": (
            "BAPTISTA, G. S. <em>GSandy</em>: software para previsão do comportamento de areias "
            "em ensaios de cisalhamento. Rio de Janeiro: PUC-Rio, 2024."
        ),
        "cite_diss": (
            "BAPTISTA, G. S. Machine Learning para Previsão do Comportamento de Areias em Ensaios "
            "de Cisalhamento Direto e DSS. 2024. Dissertação de Mestrado — Pontifícia Universidade "
            "Católica do Rio de Janeiro, Rio de Janeiro, 2024."
        ),
        "disclaimer_title": "Aviso Legal",
        "disclaimer_body": (
            "O GSandy é disponibilizado **exclusivamente para fins acadêmicos e de pesquisa**. "
            "Os modelos preditivos foram desenvolvidos e validados no contexto de uma dissertação "
            "de mestrado, com dados públicos da literatura científica.\n\n"
            "A autora **não assume qualquer responsabilidade** pelo uso dos resultados em projetos "
            "de engenharia, laudos técnicos ou tomadas de decisão. Esta ferramenta não substitui "
            "ensaios laboratoriais, avaliação profissional certificada ou normas técnicas vigentes.\n\n"
            "O uso livre para continuação de pesquisas acadêmicas é encorajado, desde que haja a "
            "devida referência aos trabalhos originais. "
            "**Toda aplicação prática é de inteira responsabilidade do usuário.**"
        ),
        "disclaimer_en_label": "*Legal notice in English:*",
        "disclaimer_en": (
            "*GSandy is provided for academic and research purposes only. "
            "The predictive models were developed and validated within a master's dissertation "
            "using publicly available scientific data. The author assumes no responsibility for "
            "the use of results in engineering projects or technical decision-making. "
            "Any practical application is entirely at the user's own risk.*"
        ),
        "contact_label": "Contato",
        "lattes_gleyce": "Lattes",
        "lattes_marina": "Lattes",
        "linkedin_gleyce": "LinkedIn",
        "linkedin_marina": "LinkedIn",
    },
    "EN": {
        "subtitle": "Sand shear test behavior simulator",
        "about_title": "About GSandy",
        "about_body": (
            "**GSandy** is an academic tool developed as part of a master's dissertation in "
            "Geotechnics at PUC-Rio (Brazil). The program uses data from direct shear and DSS "
            "tests from the scientific literature to simulate the stress × strain/displacement "
            "relationship in sands.\n\n"
            "The models employed — **Random Forest**, **SVR**, and **FNN** — were trained "
            "exclusively on sand data and validated in an academic context.\n\n"
            "For details on the methodology, refer to the dissertation "
            "*\"Machine Learning for Predicting Sand Behavior in Direct Shear and DSS Tests\"* "
            "(Baptista, 2024)."
        ),
        "sim_title": "Simulation Setup",
        "test_label": "Test type",
        "test_opts": ["DSS", "Direct Shear"],
        "gs_label": "$G_s$ — Specific gravity of solids",
        "e0_label": "$e_0$ — Initial void ratio",
        "cr_label": "$CR$ — Relative density (%)",
        "sv_label": "$\\sigma_v$ — Vertical stress (kPa)",
        "btn": "Run Simulation",
        "spinner": "Computing predictions...",
        "success": "Simulation completed.",
        "tab_chart": "Chart",
        "tab_data": "Data",
        "tab_metrics": "Metrics",
        "tab_val": "Validation",
        "tab_src": "Sources",
        "chart_title": "Predicted τ/σ",
        "model_col": "Model",
        "model_names": ["Random Forest", "SVR", "Neural Network"],
        "metrics_cap": "Performance metrics — Training and Test",
        "metrics_expand": "What do these metrics mean?",
        "metrics_help": (
            "**R²** (coefficient of determination): measures how well the model explains data "
            "variability. Ranges from 0 to 1; closer to 1 indicates a better fit.\n\n"
            "**RMSE** (root mean squared error): expressed in the same units as the target variable "
            "and penalizes large errors — lower values indicate better performance.\n\n"
            "**MAE** (mean absolute error): average of absolute deviations between predicted and "
            "actual values; represents the typical error in the original scale of the variable."
        ),
        "val_cap": "Model results on validation tests",
        "val_help": (
            "Comparison between predicted values and experimental values from validation tests "
            "(data not used in training)."
        ),
        "src_cap": "Database used for model training",
        "refs_exp": "Bibliographic References",
        "recog_title": "Awards & Publications",
        "recog_intro": (
            "GSandy and its associated dissertation have been recognized in the following "
            "publications and scientific events:"
        ),
        "tag_award": "AWARD",
        "tag_conf": "CONFERENCE",
        "tag_article": "ARTICLE",
        "tag_thesis": "DISSERTATION",
        "tag_pdf": "PDF",
        "tag_reg": "REGISTRATION",
        "cite_title": "How to Cite",
        "cite_intro": (
            "If you use GSandy or the associated dissertation in your work, "
            "please cite the references below:"
        ),
        "cite_sw_label": "Software",
        "cite_diss_label": "Dissertation",
        "cite_sw": (
            "BAPTISTA, G. S. <em>GSandy</em>: software for predicting sand behavior in shear tests. "
            "Rio de Janeiro: PUC-Rio, 2024."
        ),
        "cite_diss": (
            "BAPTISTA, G. S. Machine Learning for Predicting Sand Behavior in Direct Shear and DSS "
            "Tests. 2024. Master's Dissertation — Pontifical Catholic University of Rio de Janeiro, "
            "Rio de Janeiro, 2024."
        ),
        "disclaimer_title": "Legal Notice",
        "disclaimer_body": (
            "GSandy is provided **for academic and research purposes only**. "
            "The predictive models were developed and validated within a master's dissertation, "
            "using publicly available data from the scientific literature.\n\n"
            "The author **assumes no responsibility** for the use of results in engineering projects, "
            "technical reports, or decision-making. This tool does not replace laboratory testing, "
            "certified professional evaluation, or applicable technical standards.\n\n"
            "Free use for academic research continuation is encouraged, provided proper reference is "
            "given to the original works. "
            "**Any practical application is entirely at the user's own risk.**"
        ),
        "disclaimer_en_label": "",
        "disclaimer_en": "",
        "contact_label": "Contact",
        "lattes_gleyce": "Lattes",
        "lattes_marina": "Lattes",
        "linkedin_gleyce": "LinkedIn",
        "linkedin_marina": "LinkedIn",
    },
}

# ── Session state ──────────────────────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state.lang = "PT"

# ── Helpers ────────────────────────────────────────────────────────────────────
def get_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def t(key):
    lang = st.session_state.lang
    return TEXTS.get(lang, TEXTS["PT"]).get(key, TEXTS["PT"].get(key, f"[{key}]"))

def recog_item(tag, title, url, link_text):
    return (
        f'<div style="display:flex;align-items:flex-start;gap:0.75rem;'
        f'padding:0.8rem 0;border-bottom:1px solid #F4F4F4;">'
        f'<span style="background:#F2F2F2;color:#555;font-size:0.63rem;font-weight:700;'
        f'padding:0.2rem 0.45rem;border-radius:3px;white-space:nowrap;'
        f'text-transform:uppercase;letter-spacing:0.07em;margin-top:3px;flex-shrink:0;">'
        f'{tag}</span>'
        f'<div><div style="font-size:0.88rem;color:#111;font-weight:500;line-height:1.5;">'
        f'{title}</div>'
        f'<a href="{url}" target="_blank" '
        f'style="font-size:0.8rem;color:#777;text-decoration:none;">'
        f'{link_text} ↗</a></div></div>'
    )

def cite_box(text):
    return (
        f'<div style="background:#F8F8F8;border-radius:4px;padding:0.75rem 1rem;'
        f'font-family:\'Courier New\',monospace;font-size:0.79rem;color:#333;'
        f'margin:0.25rem 0 0.9rem 0;border-left:3px solid #DCDCDC;">'
        f'{text}</div>'
    )

# ── Header ─────────────────────────────────────────────────────────────────────
col_logo, col_title, col_lang = st.columns([0.9, 5.5, 1.6])

with col_logo:
    st.markdown(
        f"<img src='data:image/png;base64,{get_b64('logo_gsandy.png')}' "
        "style='width:48px;margin-top:8px;display:block;'>",
        unsafe_allow_html=True,
    )

with col_title:
    st.markdown("<h1 style='margin:0;padding-top:2px;'>GSandy</h1>", unsafe_allow_html=True)
    st.caption(t("subtitle"))

with col_lang:
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    lang_pick = st.radio(
        "lang", ["PT", "EN"],
        horizontal=True,
        label_visibility="collapsed",
        index=0 if st.session_state.lang == "PT" else 1,
    )
    if lang_pick != st.session_state.lang:
        st.session_state.lang = lang_pick
        st.rerun()

st.divider()

# ── About ──────────────────────────────────────────────────────────────────────
with st.expander(t("about_title"), expanded=False):
    st.markdown(t("about_body"))

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── Simulation ─────────────────────────────────────────────────────────────────
st.markdown(f"### {t('sim_title')}")

test_display = st.radio(t("test_label"), t("test_opts"), horizontal=True)
test_type = "DSS" if test_display == t("test_opts")[0] else "Cisalhamento Direto"

if test_type == "DSS":
    x_full      = "Deformação Cisalhante γ (%)" if st.session_state.lang == "PT" else "Shear Strain γ (%)"
    test_values = np.arange(0, 20, 0.7)
    result_path = "results_train/results_dss.xlsx"
    image_path  = "results_train/validation_dss.png"
    min_gs, max_gs = 2.64, 2.78
    min_cr, max_cr = 12, 100
    min_e0, max_e0 = 0.422, 1.06
    min_sv, max_sv = 6, 750
    init = [2.685, 0.808, 40, 40]
else:
    x_full      = "Deslocamento Horizontal δ (mm)" if st.session_state.lang == "PT" else "Horizontal Displacement δ (mm)"
    test_values = np.arange(0, 5, 0.3)
    result_path = "results_train/results_ds.xlsx"
    image_path  = "results_train/validation_ds.png"
    min_gs, max_gs = 2.643, 2.763
    min_cr, max_cr = 8, 100
    min_e0, max_e0 = 0.428, 0.726
    min_sv, max_sv = 13, 1600
    init = [2.656, 0.552, 64, 150]

col1, col2 = st.columns(2)
with col1:
    gs = st.number_input(t("gs_label"), min_value=min_gs, max_value=max_gs,
                         step=0.001, format="%.3f", value=init[0])
    e0 = st.number_input(t("e0_label"), min_value=min_e0, max_value=max_e0,
                         step=0.001, format="%.3f", value=init[1])
with col2:
    cr = st.number_input(t("cr_label"), min_value=min_cr, max_value=max_cr,
                         step=1, value=init[2])
    sv = st.number_input(t("sv_label"), min_value=min_sv, max_value=max_sv,
                         step=10, value=init[3])

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

if st.button(t("btn"), key="simular"):
    with st.spinner(t("spinner")):
        models = previsao_modelo.load_models_and_predict(test_type)
        rf_pred, svr_pred, nn_pred = previsao_modelo.plot_predictions(
            test_values, models, gs, e0, cr, sv
        )

    st.success(t("success"))

    names     = t("model_names")
    model_col = t("model_col")
    df = pd.DataFrame({
        x_full:    np.tile(test_values, 3),
        "τ/σ":     np.concatenate([rf_pred, svr_pred, nn_pred]),
        model_col: (names[0:1] * len(test_values)
                    + names[1:2] * len(test_values)
                    + names[2:3] * len(test_values)),
    })

    fig = px.line(
        df, x=x_full, y="τ/σ", color=model_col,
        title=t("chart_title"),
        color_discrete_sequence=["#E07B39", "#2E5EAA", "#3A9E6F"],
    )
    fig.update_traces(line=dict(width=2.5))
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Segoe UI, Arial, sans-serif", size=13),
        title=dict(font=dict(size=14, color="#222")),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor="#F2F2F2", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#F2F2F2", zeroline=False),
        margin=dict(t=60, b=40, l=40, r=20),
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        t("tab_chart"), t("tab_data"), t("tab_metrics"), t("tab_val"), t("tab_src")
    ])

    with tab1:
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.dataframe(df, use_container_width=True)

    with tab3:
        st.caption(t("metrics_cap"))
        with st.expander(t("metrics_expand")):
            st.markdown(t("metrics_help"))
        df_metrics = pd.read_excel(result_path)
        fmt = {c: "{:.3f}" for c in df_metrics.columns[1:]}
        st.dataframe(df_metrics.style.format(fmt), use_container_width=True)

    with tab4:
        st.caption(t("val_cap"))
        st.caption(t("val_help"))
        # use_column_width for compatibility with older Streamlit versions
        st.image(image_path, use_column_width=True)

    with tab5:
        st.caption(t("src_cap"))
        df_autores = pd.read_excel("fontes_autores.xlsx")
        st.dataframe(df_autores, use_container_width=True)
        with st.expander(t("refs_exp")):
            st.markdown("""
**ADAMS, R. K.** Near-Surface Response of Beach Sand: An Experimental Investigation.
Corvallis: Oregon State University, 2017.

**AL TARHOUNI, M. A.; HAWLADER, B.** Monotonic and cyclic behaviour of sand in direct
simple shear test conditions considering low stresses. *Soil Dynamics and Earthquake
Engineering*, v. 150, 2021.

**COUTINHO, J. V. M.** Ensaios de Cisalhamento Direto na Areia da Praia de Ipanema.
Dissertação de Mestrado — PUC-Rio, Rio de Janeiro, 2021.

**KIM, Y. S.** Static simple shear characteristics of Nak-dong River clean sand.
*KSCE Journal of Civil Engineering*, v. 13, n. 6, p. 389–401, 2009.

**LASHKARI, A.; FALSAFIZADEH, S. R.; RAHMAN, M. M.** Influence of linear coupling between
volumetric and shear strains on instability and post-peak softening of sand in direct
simple shear tests. *Acta Geotechnica*, v. 16, n. 11, 2021.

**LASHKARI, A.; FALSAFIZADEH, S. R.; SHOURIJEH, P. T.; ALIPOUR, M. J.** Instability of
loose sand in constant volume direct simple shear tests in relation to particle shape.
*Acta Geotechnica*, v. 15, n. 9, 2020.

**MARQUES, F. DE L.** Ensaios de resistência ao cisalhamento com areia de Hokksund para
projeto de revitalização da câmara de calibração. UFRJ/FAPERJ, Rio de Janeiro, 2009.

**MONTEIRO, D. P.; DANZIGER, B. R.; LIMA, B. T.** Caracterização Geotécnica da Areia do
Porto do Açu. *10º Seminário de Engenharia de Fundações Especiais e Geotecnia*, 2023.

**NUNES, V. P.** Ensaios de Caracterização Geotécnica da Areia da Praia de Itaipuaçu.
Projeto de Graduação — UFRJ, Rio de Janeiro, 2014.

**PINHEIRO, G. P.** Caracterização Geotécnica em Laboratório da Areia da Praia dos
Cavaleiros–Macaé/RJ. UFRJ, 2018.

**SIMÕES, F. B.** Caracterização Geotécnica da Areia da Praia de Ipanema.
Projeto de Graduação — UFRJ, Rio de Janeiro, 2015.

**SCHUCK, T. E. DE S.** Ensaios de cisalhamento simples na areia da Praia de Ipanema.
Dissertação de Mestrado — PUC-Rio, Rio de Janeiro, 2022.

**TELES, G. L. V.** Estudo Sobre os Parâmetros de Resistência e Deformabilidade da
Areia de Hokksund. Projeto de Graduação — UFRJ, Rio de Janeiro, 2013.

**VAID, Y. P.; SIVATHAYALAN, S.** Static and cyclic liquefaction potential of Fraser Delta
sand in simple shear and triaxial tests. *Canadian Geotechnical Journal*, v. 33, 1996.

**ZORZAN, L. G.** Resistência ao Cisalhamento do Solo pelos Ensaios de Cisalhamento
Direto e DSS: Análise Experimental e Aplicação na Estabilidade de Taludes.
TCC — UFPR, Curitiba, 2018.
""")

st.divider()

# ── Recognition & Publications ─────────────────────────────────────────────────
with st.expander(t("recog_title"), expanded=False):
    st.caption(t("recog_intro"))
    st.markdown(
        recog_item(
            t("tag_award"),
            "XIII Prêmio CREA-RJ de Trabalhos Científicos e Tecnológicos 2025",
            "https://crea-rj.org.br/wp-content/uploads/2025/12/E-BOOK-TCT-2025.pdf",
            "Ver publicação (pág. 48)",
        ) +
        recog_item(
            t("tag_conf"),
            "COBRAMSEG 2024 — Trabalho aprovado e apresentado",
            "https://2024.cobramseg.com.br/evento/cobramseg2024/trabalhosaprovados/naintegra/741",
            "Acessar trabalho",
        ) +
        recog_item(
            t("tag_article"),
            "Artigo publicado — Soils and Rocks",
            "https://soilsandrocks.com/sr-2026-012125",
            "Acessar artigo",
        ) +
        recog_item(
            t("tag_thesis"),
            "Dissertação — Acervo Maxwell PUC-Rio",
            "https://www.maxwell.vrac.puc-rio.br/colecao.php?strSecao=resultado&nrSeq=68591&idi=1&rc=1",
            "Acessar acervo",
        ) +
        recog_item(
            t("tag_pdf"),
            "Trabalho completo (Google Drive)",
            "https://drive.google.com/file/d/1vq4Hce54fZIJ4fo1IfJ1pWnK0xmn0QR_/view",
            "Acessar PDF",
        ) +
        recog_item(
            t("tag_reg"),
            "Registro de programa de computador",
            "#",  # substituir pelo link do registro quando disponível
            "Acessar registro",
        ) +
        "<div style='height:2px'></div>",
        unsafe_allow_html=True,
    )

# ── How to Cite ────────────────────────────────────────────────────────────────
with st.expander(t("cite_title"), expanded=False):
    st.caption(t("cite_intro"))
    st.markdown(f"**{t('cite_sw_label')}**")
    st.markdown(cite_box(t("cite_sw")), unsafe_allow_html=True)
    st.markdown(f"**{t('cite_diss_label')}**")
    st.markdown(cite_box(t("cite_diss")), unsafe_allow_html=True)

# ── Disclaimer ─────────────────────────────────────────────────────────────────
with st.expander(t("disclaimer_title"), expanded=False):
    st.markdown(t("disclaimer_body"))
    if st.session_state.lang == "PT" and t("disclaimer_en"):
        st.markdown("---")
        st.markdown(t("disclaimer_en_label"))
        st.markdown(t("disclaimer_en"))

# ── Footer ─────────────────────────────────────────────────────────────────────
LATTES_GLEYCE   = "#"   # substituir pelo link do Lattes
LATTES_MARINA   = "#"
LINKEDIN_GLEYCE = "#"   # substituir pelo link do LinkedIn
LINKEDIN_MARINA = "#"

st.markdown(f"""
<div style="text-align:center;padding:1.5rem 0 1rem;color:#888;font-size:0.8rem;
            border-top:1px solid #F0F0F0;margin-top:2rem;line-height:1.8;">
  <strong style="color:#333;">{t("contact_label")}</strong><br><br>
  <strong style="color:#444;">Gleyce Souza Baptista</strong>
  &nbsp;&middot;&nbsp;
  <a href="mailto:gleycesouzaa@gmail.com" style="color:#666;text-decoration:none;">gleycesouzaa@gmail.com</a>
  &nbsp;&middot;&nbsp;
  <a href="{LATTES_GLEYCE}" target="_blank" style="color:#666;text-decoration:none;">{t("lattes_gleyce")}</a>
  &nbsp;&middot;&nbsp;
  <a href="{LINKEDIN_GLEYCE}" target="_blank" style="color:#666;text-decoration:none;">{t("linkedin_gleyce")}</a>
  <br>
  <strong style="color:#444;">Marina Bellaver Corte</strong>
  &nbsp;&middot;&nbsp;
  <a href="mailto:marinabellaver@gmail.com" style="color:#666;text-decoration:none;">marinabellaver@gmail.com</a>
  &nbsp;&middot;&nbsp;
  <a href="{LATTES_MARINA}" target="_blank" style="color:#666;text-decoration:none;">{t("lattes_marina")}</a>
  &nbsp;&middot;&nbsp;
  <a href="{LINKEDIN_MARINA}" target="_blank" style="color:#666;text-decoration:none;">{t("linkedin_marina")}</a>
  <br><br>
  <span style="color:#BBB;font-size:0.75rem;">
    Pontifícia Universidade Católica do Rio de Janeiro
    &nbsp;&middot;&nbsp;
    Universidade Federal do Rio Grande do Sul
    &nbsp;&middot;&nbsp;
    Geotecnia, 2024
  </span>
</div>
""", unsafe_allow_html=True)
