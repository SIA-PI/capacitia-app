import plotly.io as pio
import streamlit as st
from pathlib import Path

ASSETS_DIR = Path(__file__).parent / "assets"
CSS_FILE = ASSETS_DIR / "theme.css"

def configure_plotly_theme():
    pio.templates["capacit_dark"] = pio.templates["plotly_dark"]
    tpl = pio.templates["capacit_dark"]
    tpl.layout.font.family = "Inter, Segoe UI, Roboto, Arial"
    tpl.layout.colorway = [
        "#7DD3FC", "#34D399", "#FBBF24", "#F472B6", "#60A5FA", "#A78BFA", "#F87171"
    ]
    tpl.layout.paper_bgcolor = "#0f1220"
    tpl.layout.plot_bgcolor = "#11142a"
    tpl.layout.hoverlabel = dict(
        bgcolor="#0f1220", font_size=12, font_family="Inter, Segoe UI, Roboto, Arial"
    )
    pio.templates.default = "capacit_dark"

def inject_css():
    if CSS_FILE.exists():
        css = CSS_FILE.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    else:
        st.warning("Arquivo CSS não encontrado em assets/theme.css")