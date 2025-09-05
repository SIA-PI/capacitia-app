from datetime import datetime
from pathlib import Path

import streamlit as st

from app.theme import configure_plotly_theme, inject_css
from app.data.repository import DataRepository
from app.data.sources import DEFAULT_CANDIDATES
from app.domain.kpis import fmt_int_br
from app.charts.common import nz
from app.pages import visao_geral, cargos, secretarias, eventos


# =========================
# CONFIG & THEME
# =========================
st.set_page_config(
    page_title="Dashboard CapacitIA",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)
configure_plotly_theme()
inject_css()

# =========================
# DATA LOAD
# =========================
DEFAULT_XLSX = next((p for p in DEFAULT_CANDIDATES if p.exists()), DEFAULT_CANDIDATES[0])
if not DEFAULT_XLSX.exists():
    st.error(
        "Arquivo Excel não encontrado. Verifique estes caminhos:\n"
        + "\n".join(str(p) for p in DEFAULT_CANDIDATES)
    )
    st.stop()

repo = DataRepository(DEFAULT_XLSX)
repo.load()

# =========================
# KPIs (a partir da VISÃO ABERTA / TOTAL GERAL)
# =========================
tot_insc, tot_cert, taxa_cert, sec_atendidas = repo.get_kpis()

# =========================
# HEADER
# =========================
st.markdown(
    f"""
<div class="hero">
  <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;">
    <div>
      <div style="font-size:2.0rem;font-weight:800;letter-spacing:.3px;">🚀 Dashboard CapacitIA</div>
      <div style="color:#a6accd;">Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)
c1.markdown(
    f'<div class="kpi"><h4>Total de Inscritos</h4><div class="val">{fmt_int_br(tot_insc)}</div></div>',
    unsafe_allow_html=True,
)
c2.markdown(
    f'<div class="kpi"><h4>Total de Certificados</h4><div class="val">{fmt_int_br(tot_cert)}</div></div>',
    unsafe_allow_html=True,
)
c3.markdown(
    f'<div class="kpi"><h4>Taxa de Certificação</h4><div class="val">{taxa_cert:.2f}%</div></div>',
    unsafe_allow_html=True,
)
c4.markdown(
    f'<div class="kpi"><h4>Secretarias atendidas</h4><div class="val">{sec_atendidas}</div></div>',
    unsafe_allow_html=True,
)
st.markdown('<div class="sep"></div>', unsafe_allow_html=True)

# =========================
# TABS
# =========================
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Visão Geral", "👥 Cargos", "🏢 Secretarias", "📚 Eventos"]
)

with tab1:
    visao_geral.render(repo)

with tab2:
    cargos.render(repo)

with tab3:
    secretarias.render(repo)

with tab4:
    eventos.render(repo)
