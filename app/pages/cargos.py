import pandas as pd
import plotly.express as px
import streamlit as st
import numpy as np

from app.charts.common import style_fig, nz

TOPN_DEFAULT = 10

def render(repo, topn: int = TOPN_DEFAULT):
    st.markdown('<div class="panel"><h4>Visão de Cargos</h4>', unsafe_allow_html=True)

    df_ev = repo.cargos_ev()
    df_rank = repo.cargos_rank()
    cargo_cols = [c for c in df_ev.columns if c not in [df_ev.columns[0], "Tipo"]]

    # Ranking
    col1, col2 = st.columns([1.65, 1])
    with col1:
        if df_rank is None or df_rank.empty:
            st.info("Sem dados para o ranking.")
        else:
            df_rank = nz(df_rank, ["Inscritos"])
            top_df = df_rank.head(topn).sort_values("Inscritos")
            if top_df.empty:
                st.info("Sem dados para o ranking.")
            else:
                fig_rank = px.bar(top_df, x="Inscritos", y=top_df.index, orientation="h",
                                  title=f"Top {topn} Cargos por Inscritos")
                st.plotly_chart(style_fig(fig_rank, height=460), use_container_width=True,
                                key=f"t2_cargos_rank_{topn}")

    # Donut
    with col2:
        if df_rank is None or df_rank.empty:
            st.info("Sem dados para o donut.")
        else:
            top_part = df_rank.head(topn).reset_index()
            top_part = nz(top_part, ["Inscritos"])
            top_part = top_part[top_part["Inscritos"] > 0]
            if top_part.empty:
                st.info("Sem dados para o donut.")
            else:
                fig_pie = px.pie(top_part, values="Inscritos", names="Cargo", hole=0.55)
                fig_pie.update_traces(textinfo="percent", textposition="inside", insidetextorientation="radial")
                fig_pie.update_layout(legend=dict(orientation="v", y=0.5, yanchor="middle", x=1.02))
                st.plotly_chart(style_fig(fig_pie, height=460), use_container_width=True,
                                key=f"t2_cargos_pie_{topn}")

    st.markdown('</div>', unsafe_allow_html=True)

    # Stacked por tipo
    st.markdown('<div class="panel"><h3>Inscritos por Cargo e Tipo de Evento</h3>', unsafe_allow_html=True)
    if not df_ev.empty:
        evento_col = df_ev.columns[0]
        df_tipo = df_ev.groupby("Tipo")[cargo_cols].sum().T.replace([np.inf, -np.inf], 0).fillna(0)
        tipos = [c for c in ["Curso de IA", "Masterclass", "Workshop"] if c in df_tipo.columns]
        if tipos:
            top_idx = df_rank.head(topn).index if df_rank is not None and not df_rank.empty else df_tipo.index
            stacked_df = df_tipo.loc[df_tipo.index.intersection(top_idx), tipos]
            stacked_df = stacked_df.loc[stacked_df.sum(axis=1).sort_values().index]
            if stacked_df.empty:
                st.info("Sem dados para o stacked.")
            else:
                fig_stacked = px.bar(stacked_df, x=tipos, y=stacked_df.index, orientation="h", barmode="stack")
                fig_stacked.update_traces(texttemplate="%{x:.0f}", textposition="inside", insidetextanchor="middle")
                st.plotly_chart(style_fig(fig_stacked), use_container_width=True, key=f"t2_cargos_stacked_{topn}")
        else:
            st.info("Tipos não encontrados em CARGOS.")
    else:
        st.info("Sem dados para o stacked.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Série por evento
    st.markdown('<div class="panel"><h3>Evolução por Evento</h3>', unsafe_allow_html=True)
    if cargo_cols:
        cargo_escolhido = st.selectbox("Escolha um cargo", cargo_cols, index=0, key="t2_cargo_series")
        evento_col = df_ev.columns[0]
        serie = (df_ev[[evento_col, "Tipo", cargo_escolhido]]
                 .rename(columns={evento_col: "Evento", cargo_escolhido: "Inscritos"}))
        serie = nz(serie, ["Inscritos"])
        if serie.empty:
            st.info("Sem dados para a série.")
        else:
            fig_series = px.bar(serie, x="Evento", y="Inscritos", color="Tipo", barmode="group", title=None)
            fig_series.update_layout(bargap=0.02, bargroupgap=0.02)
            fig_series.update_traces(marker_line_width=0)
            fig_series.update_xaxes(tickangle=-35)
            st.plotly_chart(style_fig(fig_series, height=520), use_container_width=True,
                            key=f"t2_cargos_series_{cargo_escolhido}")
    else:
        st.info("Nenhuma coluna de cargo encontrada.")
    st.markdown('</div>', unsafe_allow_html=True)
