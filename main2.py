import streamlit as st
import previsao_modelo
import base64
import pandas as pd
import plotly.express as px
import numpy as np
import urllib.parse as _up

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
  [data-testid="stAppViewContainer"] { background: #FFFFFF; }
  [data-testid="stHeader"]           { background: transparent; }
  section[data-testid="stSidebar"]   { display: none; }

  /* Global font */
  html, body, [class*="css"], p, span, div, label, input {
    font-family: 'Segoe UI', system-ui, -apple-system, Arial, sans-serif !important;
  }

  /* Typography hierarchy */
  .gs-title   { font-size:1.55rem; font-weight:700; color:#0D0D0D; letter-spacing:-0.01em; margin:0; line-height:1.2; }
  .gs-subtitle{ font-size:0.84rem; color:#777; margin-top:3px; }
  h3          { font-size:0.95rem !important; font-weight:600 !important; color:#1A1A1A !important; margin-bottom:0.2rem !important; }
  p, .stMarkdown p { font-size:0.9rem; color:#333; line-height:1.65; }
  .stCaption p     { font-size:0.82rem !important; color:#777 !important; line-height:1.5 !important; }
  .stAlert p       { font-size:0.88rem !important; }

  /* Section micro-label */
  .gs-label {
    font-size:0.67rem; font-weight:700; text-transform:uppercase;
    letter-spacing:0.12em; color:#BBBBBB;
    padding-bottom:0.45rem; border-bottom:1px solid #F2F2F2;
    margin:0.2rem 0 0.4rem 0;
  }

  /* Tab font */
  [data-baseweb="tab"] { font-size:0.87rem !important; font-weight:500 !important; }
  [data-baseweb="tab-list"] { gap:0.5rem !important; }

  /* Divider */
  hr { border-color:#F2F2F2 !important; margin:0.6rem 0 !important; }

  /* Button */
  .stButton > button {
    background:#1B2B3A !important; color:#fff !important;
    border:none !important; border-radius:5px !important;
    padding:0.52rem 1.4rem !important;
    font-size:0.88rem !important; font-weight:500 !important;
    width:100% !important; letter-spacing:0.025em !important;
    transition:background 0.15s !important;
  }
  .stButton > button:hover { background:#2D4A63 !important; }
  .stButton > button p,
  .stButton > button span,
  .stButton > button * { color: #FFFFFF !important; }

  /* Expanders */
  [data-testid="stExpander"] {
    border:1px solid #EBEBEB !important; border-radius:6px !important;
    background:#FDFDFD !important;
  }
  [data-testid="stExpander"] summary p {
    font-size:0.89rem !important; font-weight:500 !important; color:#222 !important;
  }

  /* Inputs */
  .stNumberInput label { font-size:0.86rem !important; color:#444 !important; }
  .stRadio    > label  { font-size:0.86rem !important; color:#444 !important; }
  .stRadio    label    { font-size:0.86rem !important; }

  /* Language toggle */
  .gs-lang-toggle {
    display:flex; gap:6px; justify-content:flex-end; align-items:center;
  }
  .gs-lang-btn {
    display:inline-flex; align-items:center; gap:5px;
    font-size:0.73rem; font-weight:700; padding:4px 9px;
    border-radius:4px; border:1px solid #DDD; cursor:pointer;
    background:#F7F7F7; color:#666; text-decoration:none;
    letter-spacing:0.05em; line-height:1;
  }
  .gs-lang-btn.active { background:#1B2B3A; color:#FFF; border-color:#1B2B3A; }
  .gs-lang-btn svg { flex-shrink:0; }

  /* Recognition items */
  .gs-recog-item {
    display:flex; align-items:flex-start; gap:0.75rem;
    padding:0.75rem 0; border-bottom:1px solid #F5F5F5;
  }
  .gs-recog-tag {
    background:#F2F2F2; color:#555; font-size:0.62rem; font-weight:700;
    padding:0.18rem 0.45rem; border-radius:3px; white-space:nowrap;
    text-transform:uppercase; letter-spacing:0.07em;
    margin-top:3px; flex-shrink:0;
  }
  .gs-recog-title { font-size:0.88rem; color:#111; font-weight:500; line-height:1.5; }
  .gs-recog-link  { font-size:0.79rem; color:#777; text-decoration:none; }
  .gs-recog-link:hover { color:#1B2B3A; }

  /* Dissertation card */
  .gs-diss-card {
    background:#FAFAFA; border-radius:6px; padding:1rem 1.1rem;
    border:1px solid #EBEBEB; margin-bottom:0.4rem;
  }
  .gs-diss-title { font-size:0.9rem; font-weight:600; color:#111; line-height:1.6; }
  .gs-diss-meta  { font-size:0.81rem; color:#666; margin-top:0.35rem; line-height:1.6; }
  .gs-diss-links { margin-top:0.6rem; display:flex; gap:1rem; flex-wrap:wrap; }

  /* Cite box */
  .gs-cite {
    background:#F8F8F8; border-radius:4px; padding:0.75rem 1rem;
    font-family:'Courier New',monospace; font-size:0.78rem; color:#333;
    margin:0.2rem 0 0.85rem 0; border-left:3px solid #DCDCDC; line-height:1.55;
  }

  /* Note text */
  .gs-note { font-size:0.77rem; color:#999; margin:0.5rem 0 0 0; line-height:1.5; }

  @media (max-width:640px) {
    .gs-title { font-size:1.25rem; }
    .stButton > button { font-size:0.84rem !important; }
  }
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
DISSERTATION_DOI  = "https://doi.org/10.17771/PUCRio.acad.68591"
DISS_MAXWELL_URL  = "https://www.maxwell.vrac.puc-rio.br/colecao.php?strSecao=resultado&nrSeq=68591&idi=1&rc=1"
DISS_DEFENSE_DATE = "Rio de Janeiro, 16 de abril de 2024"
DISS_ADVISOR      = "Marina Bellaver Corte, DSc."
DISS_COMMITTEE    = [
    "Profª. Marina Bellaver Corte — Orientadora e Presidente, PUC-Rio",
    "Profª. Raquel Quadros Velloso — PUC-Rio",
    "Prof. Gustavo Vaz de Mello Guimarães — UFRJ",
]

LATTES_GLEYCE   = "http://lattes.cnpq.br/9284309506959502"
LATTES_MARINA   = "http://lattes.cnpq.br/3293171632352740"
LINKEDIN_GLEYCE = "https://www.linkedin.com/in/gleyce-souza/"
LINKEDIN_MARINA = "https://www.linkedin.com/in/marinabellavercorte/"

# (tag_key, url_primary, link_key_primary, url_secondary_or_None, link_key_secondary_or_None)
RECOG_DATA = [
    ("tag_article", "https://soilsandrocks.com/sr-2026-012125",
     "link_article", None, None),
    ("tag_award",   "https://crea-rj.org.br/wp-content/uploads/2025/12/E-BOOK-TCT-2025.pdf",
     "link_award",   "https://drive.google.com/file/d/1vq4Hce54fZIJ4fo1IfJ1pWnK0xmn0QR_/view", "link_award2"),
    ("tag_conf",    "https://2024.cobramseg.com.br/evento/cobramseg2024/trabalhosaprovados/naintegra/741",
     "link_conf",    None, None),
    ("tag_reg",     "https://busca.inpi.gov.br/pePI/",
     "link_reg",     None, None),
]

def _svg_uri(svg: str) -> str:
    return "url('data:image/svg+xml," + _up.quote(svg, safe='') + "')"

_CSS_BR_URI = _svg_uri(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="none">'
    '<rect x="1" y="1" width="18" height="18" rx="3.5" stroke="#777" stroke-width="1.5"/>'
    '<path d="M10 3.5L18 10L10 16.5L2 10Z" stroke="#777" stroke-width="1.5" fill="none"/>'
    '<circle cx="10" cy="10" r="3.3" stroke="#777" stroke-width="1.5" fill="none"/>'
    '</svg>'
)
_CSS_US_URI = _svg_uri(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 28 20" fill="none">'
    '<rect x="1" y="1" width="26" height="18" rx="3.5" stroke="#777" stroke-width="1.5"/>'
    '<line x1="1.7" y1="4.2" x2="26.3" y2="4.2" stroke="#777" stroke-width="0.9" stroke-opacity=".4"/>'
    '<line x1="1.7" y1="7.2" x2="26.3" y2="7.2" stroke="#777" stroke-width="0.9" stroke-opacity=".4"/>'
    '<line x1="1.7" y1="10.2" x2="26.3" y2="10.2" stroke="#777" stroke-width="0.9" stroke-opacity=".4"/>'
    '<line x1="1.7" y1="13.2" x2="26.3" y2="13.2" stroke="#777" stroke-width="0.9" stroke-opacity=".4"/>'
    '<line x1="1.7" y1="16.2" x2="26.3" y2="16.2" stroke="#777" stroke-width="0.9" stroke-opacity=".4"/>'
    '</svg>'
)

st.markdown(
    f"<style>"
    f"[data-testid='stRadio'] [data-baseweb='radio']:first-child p::before,"
    f"[data-testid='stRadioGroup'] label:first-child p::before{{"
    f"content:'';display:inline-block;width:16px;height:13px;"
    f"background-image:{_CSS_BR_URI};background-size:contain;"
    f"background-repeat:no-repeat;background-position:center;"
    f"vertical-align:middle;margin-right:4px;margin-bottom:1px;}}"
    f"[data-testid='stRadio'] [data-baseweb='radio']:nth-child(2) p::before,"
    f"[data-testid='stRadioGroup'] label:nth-child(2) p::before{{"
    f"content:'';display:inline-block;width:22px;height:13px;"
    f"background-image:{_CSS_US_URI};background-size:contain;"
    f"background-repeat:no-repeat;background-position:center;"
    f"vertical-align:middle;margin-right:4px;margin-bottom:1px;}}"
    f"[data-testid='stTabsContent'] [data-testid='stRadio'] [data-baseweb='radio'] p::before,"
    f"[data-testid='stTabsContent'] [data-testid='stRadioGroup'] label p::before{{"
    f"content:none!important;display:none!important;}}"
    f"</style>",
    unsafe_allow_html=True,
)

# ── Bilingual texts ────────────────────────────────────────────────────────────
TEXTS = {
    "PT": {
        "subtitle":      "Simulador de ensaios de cisalhamento em areias",
        "nav_sim":       "Simulação",
        "nav_model":     "Modelo",
        "nav_about":     "Publicações",
        "about_title":   "Sobre o GSandy",
        "about_body": (
            "O **GSandy** é uma ferramenta acadêmica desenvolvida como parte de dissertação "
            "de mestrado em Geotecnia pela PUC-Rio. O programa utiliza dados de ensaios de "
            "cisalhamento direto e DSS da literatura científica para simular a relação "
            "tensão × deformação/deslocamento em areias.\n\n"
            "Os modelos empregados — **Random Forest**, **SVR** e **FNN** — foram treinados "
            "exclusivamente com dados de areia e validados em contexto acadêmico.\n\n"
            "Para detalhes sobre a metodologia, consulte a dissertação *\"Machine Learning para "
            "Previsão do Comportamento de Areias em Ensaios de Cisalhamento Direto e DSS\"* "
            f"[(Baptista, 2024)]({DISSERTATION_DOI})."
        ),
        "sim_title":     "Configuração da Simulação",
        "test_label":    "Tipo de ensaio",
        "test_opts":     ["Cisalhamento Direto Simples (DSS)", "Cisalhamento Direto"],
        "gs_label":      "$G_s$ — Densidade real dos grãos",
        "e0_label":      "$e_0$ — Índice de vazios inicial",
        "cr_label":      "$CR$ — Compacidade Relativa (%)",
        "sv_label":      "$\\sigma_v$ — Tensão Vertical (kPa)",
        "btn":           "Simular",
        "spinner":       "Calculando previsões...",
        "success":       "Simulação concluída.",
        "tab_chart":     "Gráfico",
        "tab_data":      "Dados",
        "model_label":   "Desempenho e Transparência do Modelo",
        "tab_metrics":   "Métricas",
        "tab_val":       "Validação",
        "tab_src":       "Fontes",
        "chart_title":   "Previsão τ/σ",
        "model_col":     "Modelo",
        "model_names":   ["Random Forest", "SVR", "Rede Neural"],
        "metrics_cap":   "Métricas de desempenho — Treinamento e Teste",
        "metrics_exp":   "O que significam essas métricas?",
        "metrics_help": (
            "**R²** (coeficiente de determinação): mede o quanto o modelo explica a variabilidade "
            "dos dados. Varia de 0 a 1; quanto mais próximo de 1, melhor o ajuste.\n\n"
            "**RMSE** (raiz do erro quadrático médio): está na mesma unidade da variável alvo e "
            "penaliza erros grandes — valores menores indicam melhor desempenho.\n\n"
            "**MAE** (erro absoluto médio): média dos desvios absolutos entre previsão e valor "
            "real; representa o erro típico na escala original da variável."
        ),
        "val_cap":  "Resultados dos modelos nos ensaios de validação",
        "val_help": ("Comparação entre valores previstos e experimentais nos ensaios de validação "
                     "(dados não utilizados no treinamento)."),
        "src_cap":  "Base de dados utilizada no treinamento dos modelos",
        "refs_exp": "Referências Bibliográficas",
        "diss_section_title":  "Dissertação de Mestrado",
        "diss_full_title": (
            "Machine Learning para Previsão do Comportamento de Areias em "
            "Ensaios de Cisalhamento Direto e DSS"
        ),
        "diss_institution": "Pontifícia Universidade Católica do Rio de Janeiro",
        "diss_advisor_label":   "Orientadora",
        "diss_defense_label":   "Defesa",
        "diss_committee_label": "Banca Avaliadora",
        "diss_access": "Acervo Maxwell",
        "recog_title": "Reconhecimentos e Publicações",
        "recog_intro": ("O GSandy e a dissertação associada foram reconhecidos nas seguintes "
                        "publicações e eventos científicos:"),
        "tag_article": "ARTIGO",
        "tag_award":   "PRÊMIO",
        "tag_conf":    "CONGRESSO",
        "tag_reg":     "REGISTRO",
        "recog_titles": {
            "tag_article": "Artigo publicado — Soils and Rocks",
            "tag_award":   "XIII Prêmio CREA-RJ de Trabalhos Científicos e Tecnológicos 2025",
            "tag_conf":    "COBRAMSEG 2024 — Trabalho aprovado e apresentado",
            "tag_reg":     "Registro de programa de computador",
        },
        "link_article": "Acessar artigo",
        "link_award":   "Resumo (pág. 48)",
        "link_award2":  "PDF completo",
        "link_conf":    "Acessar trabalho",
        "link_reg":     "Acessar registro",
        "reg_note": ("Para acessar o certificado de registro: clique no link acima, selecione "
                     "<b>Continuar...</b> (sem necessidade de login) e pesquise pelo nome <b>GSandy</b>."),
        "cite_title":      "Como Citar este Trabalho",
        "cite_intro":      ("Caso utilize o GSandy ou a dissertação em seu trabalho, "
                            "cite as referências abaixo:"),
        "cite_sw_label":   "Software",
        "cite_diss_label": "Dissertação",
        "cite_sw":   ("BAPTISTA, G. S. <em>GSandy</em>: software para previsão do "
                      "comportamento de areias em ensaios de cisalhamento. "
                      "Rio de Janeiro: PUC-Rio, 2024."),
        "cite_diss": ("BAPTISTA, G. S. Machine Learning para Previsão do Comportamento de "
                      "Areias em Ensaios de Cisalhamento Direto e DSS. 2024. Dissertação de "
                      "Mestrado — Pontifícia Universidade Católica do Rio de Janeiro, "
                      "Rio de Janeiro, 2024."),
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
            "*GSandy is provided for academic and research purposes only. The predictive models "
            "were developed and validated within a master's dissertation using publicly available "
            "scientific data. The author assumes no responsibility for the use of results in "
            "engineering projects or technical decision-making. Any practical application is "
            "entirely at the user's own risk.*"
        ),
        "contact_label":       "Contato",
        "contact_gleyce":      "Gleyce de Souza Baptista, MSc.",
        "contact_gleyce_role": "Engenheira Geotécnica",
        "contact_marina":      "Marina Bellaver Corte, DSc.",
        "contact_marina_role": "Professora, UFRGS",
        "lattes_gleyce":   "Lattes",
        "lattes_marina":   "Lattes",
        "linkedin_gleyce": "LinkedIn",
        "linkedin_marina": "LinkedIn",
    },
    "EN": {
        "subtitle":      "Sand shear test behavior simulator",
        "nav_sim":       "Simulation",
        "nav_model":     "Model",
        "nav_about":     "Publications",
        "about_title":   "About GSandy",
        "about_body": (
            "**GSandy** is an academic tool developed as part of a master's dissertation in "
            "Geotechnics at PUC-Rio (Brazil). The program uses data from direct shear and DSS "
            "tests from the scientific literature to simulate the stress × strain/displacement "
            "relationship in sands.\n\n"
            "The models employed — **Random Forest**, **SVR**, and **FNN** — were trained "
            "exclusively on sand data and validated in an academic context.\n\n"
            "For details on the methodology, refer to the dissertation *\"Machine Learning for "
            "Predicting Sand Behavior in Direct Shear and DSS Tests\"* "
            f"[(Baptista, 2024)]({DISSERTATION_DOI})."
        ),
        "sim_title":     "Simulation Setup",
        "test_label":    "Test type",
        "test_opts":     ["Direct Simple Shear (DSS)", "Direct Shear"],
        "gs_label":      "$G_s$ — Specific gravity of solids",
        "e0_label":      "$e_0$ — Initial void ratio",
        "cr_label":      "$CR$ — Relative density (%)",
        "sv_label":      "$\\sigma_v$ — Vertical stress (kPa)",
        "btn":           "Run Simulation",
        "spinner":       "Computing predictions...",
        "success":       "Simulation completed.",
        "tab_chart":     "Chart",
        "tab_data":      "Data",
        "model_label":   "Model Performance & Transparency",
        "tab_metrics":   "Metrics",
        "tab_val":       "Validation",
        "tab_src":       "Sources",
        "chart_title":   "Predicted τ/σ",
        "model_col":     "Model",
        "model_names":   ["Random Forest", "SVR", "Neural Network"],
        "metrics_cap":   "Performance metrics — Training and Test",
        "metrics_exp":   "What do these metrics mean?",
        "metrics_help": (
            "**R²** (coefficient of determination): measures how well the model explains data "
            "variability. Ranges from 0 to 1; closer to 1 indicates a better fit.\n\n"
            "**RMSE** (root mean squared error): expressed in the same units as the target "
            "variable and penalizes large errors — lower values indicate better performance.\n\n"
            "**MAE** (mean absolute error): average of absolute deviations between predicted "
            "and actual values; represents the typical error in the original scale."
        ),
        "val_cap":  "Model results on validation tests",
        "val_help": ("Comparison between predicted values and experimental values from validation "
                     "tests (data not used in training)."),
        "src_cap":  "Database used for model training",
        "refs_exp": "Bibliographic References",
        "diss_section_title":  "Master's Dissertation",
        "diss_full_title": (
            "Machine Learning for Predicting Sand Behavior in "
            "Direct Shear and DSS Tests"
        ),
        "diss_institution": "Pontifical Catholic University of Rio de Janeiro",
        "diss_advisor_label":   "Advisor",
        "diss_defense_label":   "Defense",
        "diss_committee_label": "Examining Committee",
        "diss_access": "Maxwell Repository",
        "recog_title": "Awards & Publications",
        "recog_intro": ("GSandy and its associated dissertation have been recognized in the "
                        "following publications and scientific events:"),
        "tag_article": "ARTICLE",
        "tag_award":   "AWARD",
        "tag_conf":    "CONFERENCE",
        "tag_reg":     "REGISTRATION",
        "recog_titles": {
            "tag_article": "Published article — Soils and Rocks",
            "tag_award":   "XIII CREA-RJ Award for Scientific and Technological Works 2025",
            "tag_conf":    "COBRAMSEG 2024 — Approved and presented paper",
            "tag_reg":     "Software registration record",
        },
        "link_article": "Access article",
        "link_award":   "Abstract (p. 48)",
        "link_award2":  "Full paper PDF",
        "link_conf":    "Access paper",
        "link_reg":     "Access registration",
        "reg_note": ("To access the registration certificate: click the link above, select "
                     "<b>Continue...</b> (no login required), and search for <b>GSandy</b>."),
        "cite_title":      "How to Cite",
        "cite_intro":      ("If you use GSandy or the associated dissertation in your work, "
                            "please cite the references below:"),
        "cite_sw_label":   "Software",
        "cite_diss_label": "Dissertation",
        "cite_sw":   ("BAPTISTA, G. S. <em>GSandy</em>: software for predicting sand "
                      "behavior in shear tests. Rio de Janeiro: PUC-Rio, 2024."),
        "cite_diss": ("BAPTISTA, G. S. Machine Learning for Predicting Sand Behavior in "
                      "Direct Shear and DSS Tests. 2024. Master's Dissertation — Pontifical "
                      "Catholic University of Rio de Janeiro, Rio de Janeiro, 2024."),
        "disclaimer_title": "Legal Notice",
        "disclaimer_body": (
            "GSandy is provided **for academic and research purposes only**. The predictive "
            "models were developed and validated within a master's dissertation, using publicly "
            "available data from the scientific literature.\n\n"
            "The author **assumes no responsibility** for the use of results in engineering "
            "projects, technical reports, or decision-making. This tool does not replace "
            "laboratory testing, certified professional evaluation, or applicable technical "
            "standards.\n\n"
            "Free use for academic research continuation is encouraged, provided proper "
            "reference is given to the original works. "
            "**Any practical application is entirely at the user's own risk.**"
        ),
        "disclaimer_en_label": "",
        "disclaimer_en": "",
        "contact_label":       "Contact",
        "contact_gleyce":      "Gleyce de Souza Baptista, MSc.",
        "contact_gleyce_role": "Geotechnical Engineer",
        "contact_marina":      "Marina Bellaver Corte, DSc.",
        "contact_marina_role": "Professor, UFRGS",
        "lattes_gleyce":   "Lattes",
        "lattes_marina":   "Lattes",
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

def safe_rerun():
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()

def recog_item(tag, title, url1, link1, url2=None, link2=None, note=None):
    links = f'<a class="gs-recog-link" href="{url1}" target="_blank">{link1} ↗</a>'
    if url2 and link2:
        links += f'&nbsp;&middot;&nbsp;<a class="gs-recog-link" href="{url2}" target="_blank">{link2} ↗</a>'
    note_html = (
        f'<div style="font-size:0.71rem;color:#AAA;margin-top:5px;line-height:1.5;">{note}</div>'
    ) if note else ''
    return (
        f'<div class="gs-recog-item">'
        f'<span class="gs-recog-tag">{tag}</span>'
        f'<div><div class="gs-recog-title">{title}</div>{links}{note_html}</div>'
        f'</div>'
    )

def cite_box(text):
    return f'<div class="gs-cite">{text}</div>'

def section_label(text):
    st.markdown(f'<p class="gs-label">{text}</p>', unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
col_logo, col_title, col_lang = st.columns([0.9, 5.5, 1.6])

with col_logo:
    st.markdown(
        f"<img src='data:image/png;base64,{get_b64('logo_gsandy.png')}' "
        "style='width:46px;margin-top:6px;display:block;'>",
        unsafe_allow_html=True,
    )

with col_title:
    st.markdown(f"<p class='gs-title'>GSandy</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='gs-subtitle'>{t('subtitle')}</p>", unsafe_allow_html=True)

with col_lang:
    lang_pick = st.radio(
        "lang", ["PT", "EN"],
        horizontal=True,
        label_visibility="collapsed",
        index=0 if st.session_state.lang == "PT" else 1,
    )
    if lang_pick != st.session_state.lang:
        st.session_state.lang = lang_pick
        safe_rerun()

st.divider()

# ── Navigation ─────────────────────────────────────────────────────────────────
tab_sim, tab_model, tab_pub = st.tabs([t("nav_sim"), t("nav_model"), t("nav_about")])


# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONTENT FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def _page_sim():
    with st.expander(t("about_title"), expanded=False):
        st.markdown(t("about_body"))

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown(f"### {t('sim_title')}")

    test_display = st.radio(t("test_label"), t("test_opts"), horizontal=True)
    test_type = "DSS" if test_display == t("test_opts")[0] else "Cisalhamento Direto"

    if test_type == "DSS":
        x_full      = "Deformação Cisalhante γ (%)" if st.session_state.lang == "PT" else "Shear Strain γ (%)"
        test_values = np.arange(0, 20, 0.7)
        min_gs, max_gs = 2.64, 2.78
        min_cr, max_cr = 12, 100
        min_e0, max_e0 = 0.422, 1.06
        min_sv, max_sv = 6, 750
        init = [2.685, 0.808, 40, 40]
    else:
        x_full      = "Deslocamento Horizontal δ (mm)" if st.session_state.lang == "PT" else "Horizontal Displacement δ (mm)"
        test_values = np.arange(0, 5, 0.3)
        min_gs, max_gs = 2.643, 2.763
        min_cr, max_cr = 8, 100
        min_e0, max_e0 = 0.428, 0.726
        min_sv, max_sv = 13, 1600
        init = [2.656, 0.552, 64, 150]

    st.session_state["_last_test_type"] = test_type

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

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    if st.button(t("btn"), key="simular"):
        try:
            with st.spinner(t("spinner")):
                models = previsao_modelo.load_models_and_predict(test_type)
                rf_pred, svr_pred, nn_pred = previsao_modelo.plot_predictions(
                    test_values, models, gs, e0, cr, sv
                )
            names     = t("model_names")
            model_col = t("model_col")
            df = pd.DataFrame({
                x_full:    np.tile(test_values, 3),
                "τ/σ":     np.concatenate([rf_pred, svr_pred, nn_pred]),
                model_col: (names[0:1] * len(test_values)
                            + names[1:2] * len(test_values)
                            + names[2:3] * len(test_values)),
            })
            params_sub = (
                f"G<sub>s</sub>={gs:.3f} · "
                f"e<sub>0</sub>={e0:.3f} · "
                f"CR={cr}% · "
                f"σ<sub>v</sub>={sv} kPa"
            )
            fig = px.line(
                df, x=x_full, y="τ/σ", color=model_col,
                title=f"{t('chart_title')} — {test_display}<br><sup>{params_sub}</sup>",
                color_discrete_sequence=["#1E4B9C", "#6BAED6", "#C44040"],
            )
            st.session_state["_sim_params"] = {
                "gs": gs, "e0": e0, "cr": cr, "sv": sv,
                "test_display": test_display,
            }
            fig.update_traces(line=dict(width=2, dash="dash"))
            fig.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                font=dict(family="Segoe UI, Arial, sans-serif", size=13),
                title=dict(font=dict(size=14, color="#222")),
                legend=dict(
                    title=dict(text=t("model_col"),
                               font=dict(size=11, color="#999")),
                    orientation="v",
                    yanchor="top", y=1,
                    xanchor="left", x=1.02,
                    borderwidth=0,
                    bgcolor="rgba(0,0,0,0)",
                ),
                xaxis=dict(showgrid=True, gridcolor="#F2F2F2",
                           zeroline=False, title_font=dict(size=12)),
                yaxis=dict(showgrid=True, gridcolor="#F2F2F2",
                           zeroline=False, title_font=dict(size=12)),
                margin=dict(t=50, b=40, l=50, r=120),
            )
            st.session_state["_sim_df"]  = df
            st.session_state["_sim_fig"] = fig
            st.session_state["_sim_ok"]  = True
        except Exception as err:
            st.error(f"{'Erro na simulação' if st.session_state.lang == 'PT' else 'Simulation error'}: {err}")
            st.session_state["_sim_ok"] = False

    if st.session_state.get("_sim_ok"):
        tab_chart, tab_data = st.tabs([t("tab_chart"), t("tab_data")])
        with tab_chart:
            st.plotly_chart(st.session_state["_sim_fig"], use_container_width=True)
        with tab_data:
            p = st.session_state.get("_sim_params", {})
            if p:
                st.caption(
                    f"{p.get('test_display', '')} · "
                    f"Gₛ={p['gs']:.3f} · e₀={p['e0']:.3f} · "
                    f"CR={p['cr']}% · σᵥ={p['sv']} kPa"
                )
            st.dataframe(st.session_state["_sim_df"], use_container_width=True)


def _page_model():
    _tt = st.session_state.get("_last_test_type", "DSS")
    if _tt == "DSS":
        result_path = "results_train/results_dss.xlsx"
        image_path  = "results_train/validation_dss.png"
    else:
        result_path = "results_train/results_ds.xlsx"
        image_path  = "results_train/validation_ds.png"

    # ── Métricas ──────────────────────────────────────────────────────────────
    section_label(t("tab_metrics"))
    st.caption(t("metrics_cap"))
    with st.expander(t("metrics_exp")):
        st.markdown(t("metrics_help"))
    try:
        df_m = pd.read_excel(result_path)
        fmt  = {c: "{:.3f}" for c in df_m.columns[1:]}
        st.dataframe(df_m.style.format(fmt), use_container_width=True)
    except Exception as e:
        st.error(str(e))

    st.divider()

    # ── Validação ─────────────────────────────────────────────────────────────
    section_label(t("tab_val"))
    st.caption(t("val_cap"))
    st.caption(t("val_help"))
    try:
        st.image(image_path, use_container_width=True)
    except Exception as e:
        st.error(str(e))

    st.divider()

    # ── Fontes ────────────────────────────────────────────────────────────────
    section_label(t("tab_src"))
    st.caption(t("src_cap"))
    try:
        df_aut = pd.read_excel("fontes_autores.xlsx")
        st.dataframe(df_aut, use_container_width=True)
    except Exception as e:
        st.error(str(e))
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

**MARQUES, F. DE L.** Ensaios de resistência ao cisalhamento com areia de Hokksund.
UFRJ/FAPERJ, Rio de Janeiro, 2009.

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
Direto e DSS. TCC — UFPR, Curitiba, 2018.
""")


def _page_pub():
    # ── Dissertation ──────────────────────────────────────────────────────────
    section_label(t("diss_section_title"))
    _author_pt = "Gleyce de Souza Baptista"
    st.markdown(
        f'<div class="gs-diss-card">'
        f'<div class="gs-diss-title">{t("diss_full_title")}</div>'
        f'<div class="gs-diss-meta">'
        f'{_author_pt} &mdash; {t("diss_institution")}, {DISS_DEFENSE_DATE}'
        f'</div>'
        f'<div class="gs-diss-meta">'
        f'<b>{t("diss_advisor_label")}:</b> {DISS_ADVISOR}'
        f'</div>'
        f'<div class="gs-diss-links">'
        f'<a class="gs-recog-link" href="{DISS_MAXWELL_URL}" target="_blank">'
        f'{t("diss_access")} ↗</a>'
        f'<a class="gs-recog-link" href="{DISSERTATION_DOI}" target="_blank">'
        f'DOI ↗</a>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    if DISS_COMMITTEE:
        with st.expander(t("diss_committee_label")):
            for member in DISS_COMMITTEE:
                st.markdown(f"- {member}")

    st.divider()

    # ── Awards & Publications ─────────────────────────────────────────────────
    section_label(t("recog_title"))
    st.caption(t("recog_intro"))
    recog_titles = t("recog_titles")
    items_html = ""
    for tk, url1, lk1, url2, lk2 in RECOG_DATA:
        title = recog_titles.get(tk, "")
        l1    = t(lk1)
        l2    = t(lk2) if lk2 else None
        note  = t("reg_note") if tk == "tag_reg" else None
        items_html += recog_item(t(tk), title, url1, l1, url2, l2, note=note)
    items_html += "<div style='height:2px'></div>"
    st.markdown(items_html, unsafe_allow_html=True)

    st.divider()

    # ── How to Cite ───────────────────────────────────────────────────────────
    section_label(t("cite_title"))
    st.caption(t("cite_intro"))
    st.markdown(f"**{t('cite_sw_label')}**")
    st.markdown(cite_box(t("cite_sw")), unsafe_allow_html=True)
    st.markdown(f"**{t('cite_diss_label')}**")
    st.markdown(cite_box(t("cite_diss")), unsafe_allow_html=True)

    st.divider()

    # ── Disclaimer ────────────────────────────────────────────────────────────
    with st.expander(t("disclaimer_title"), expanded=False):
        st.markdown(t("disclaimer_body"))
        if st.session_state.lang == "PT" and t("disclaimer_en"):
            st.markdown("---")
            st.markdown(t("disclaimer_en_label"))
            st.markdown(t("disclaimer_en"))


# ── Dispatch ────────────────────────────────────────────────────────────────────
with tab_sim:   _page_sim()
with tab_model: _page_model()
with tab_pub:   _page_pub()


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center;padding:1.5rem 0 0.8rem;
            border-top:1px solid #F0F0F0;margin-top:1.5rem;line-height:1.95;">
  <span style="font-size:0.67rem;font-weight:700;text-transform:uppercase;
               letter-spacing:0.12em;color:#CCC;">{t("contact_label")}</span>
  <br><br>
  <strong style="color:#444;font-size:0.82rem;">{t("contact_gleyce")}</strong>
  <span style="color:#C0C0C0;font-size:0.74rem;"> &mdash; {t("contact_gleyce_role")}</span><br>
  <a href="mailto:gleycesouzaa@gmail.com" style="color:#666;text-decoration:none;font-size:0.8rem;">gleycesouzaa@gmail.com</a>
  &nbsp;&middot;&nbsp;
  <a href="{LATTES_GLEYCE}" target="_blank" style="color:#666;text-decoration:none;font-size:0.8rem;">{t("lattes_gleyce")}</a>
  &nbsp;&middot;&nbsp;
  <a href="{LINKEDIN_GLEYCE}" target="_blank" style="color:#666;text-decoration:none;font-size:0.8rem;">{t("linkedin_gleyce")}</a>
  <br>
  <strong style="color:#444;font-size:0.82rem;">{t("contact_marina")}</strong>
  <span style="color:#C0C0C0;font-size:0.74rem;"> &mdash; {t("contact_marina_role")}</span><br>
  <a href="mailto:marinabellaver@gmail.com" style="color:#666;text-decoration:none;font-size:0.8rem;">marinabellaver@gmail.com</a>
  &nbsp;&middot;&nbsp;
  <a href="{LATTES_MARINA}" target="_blank" style="color:#666;text-decoration:none;font-size:0.8rem;">{t("lattes_marina")}</a>
  &nbsp;&middot;&nbsp;
  <a href="{LINKEDIN_MARINA}" target="_blank" style="color:#666;text-decoration:none;font-size:0.8rem;">{t("linkedin_marina")}</a>
  <br><br>
  <span style="color:#CCC;font-size:0.73rem;">
    Pontifícia Universidade Católica do Rio de Janeiro, 2024
    &nbsp;&middot;&nbsp;
    Universidade Federal do Rio Grande do Sul, 2026
  </span>
</div>
""", unsafe_allow_html=True)
