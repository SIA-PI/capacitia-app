import pandas as pd
import plotly.express as px
import streamlit as st

from app.charts.common import style_fig, nz
from app.domain.filters import drop_empty_labels


TOPN_DEFAULT = 10

def render(repo, topn: int = TOPN_DEFAULT):
    df_f = repo.secretarias_filtered()
    df_f = drop_empty_labels(df_f, "SECRETARIA/ÓRGÃO")

    colA, colB = st.columns(2)

    with colA:
        st.markdown('<div class="panel"><h3>Desempenho por Secretaria</h3>', unsafe_allow_html=True)
        grp_sec = (
            df_f.groupby("SECRETARIA/ÓRGÃO")[["Nº INSCRITOS", "Nº CERTIFICADOS"]]
                .sum()
                .sort_values("Nº INSCRITOS", ascending=False)
        )
        grp_sec["Taxa de Permanência (%)"] = (
            grp_sec["Nº CERTIFICADOS"] / grp_sec["Nº INSCRITOS"]
        ).replace([pd.NA, float("inf")], 0).fillna(0) * 100

        modo = st.radio(
            "Visualizar",
            ["Inscritos", "Certificados", "Taxa de Permanência", "Comparativo"],
            horizontal=True, key="rg_sec",
        )

        if modo == "Inscritos":
            d = nz(grp_sec, ["Nº INSCRITOS"]).head(topn).sort_values("Nº INSCRITOS")
            if d.empty:
                st.info("Sem dados para plotar.")
                fig = px.bar(pd.DataFrame({"Nº INSCRITOS": []}), x="Nº INSCRITOS", y=[])
            else:
                fig = px.bar(d, x="Nº INSCRITOS", y=d.index, orientation="h", title="Top por Inscritos")

        elif modo == "Certificados":
            d = nz(grp_sec, ["Nº CERTIFICADOS"]).sort_values("Nº CERTIFICADOS", ascending=False) \
                                               .head(topn).sort_values("Nº CERTIFICADOS")
            if d.empty:
                st.info("Sem dados para plotar.")
                fig = px.bar(pd.DataFrame({"Nº CERTIFICADOS": []}), x="Nº CERTIFICADOS", y=[])
            else:
                fig = px.bar(d, x="Nº CERTIFICADOS", y=d.index, orientation="h", title="Top por Certificados")

        elif modo == "Taxa de Permanência":
            base = grp_sec[grp_sec["Nº INSCRITOS"] > 0]
            d = nz(base, ["Taxa de Permanência (%)"]).sort_values("Taxa de Permanência (%)", ascending=False) \
                                                    .head(topn).sort_values("Taxa de Permanência (%)")
            if d.empty:
                st.info("Sem dados para plotar.")
                fig = px.bar(pd.DataFrame({"Taxa de Permanência (%)": []}), x="Taxa de Permanência (%)", y=[])
            else:
                fig = px.bar(d, x="Taxa de Permanência (%)", y=d.index, orientation="h", title="Top por Permanência")

        else:  # Comparativo
            d = nz(grp_sec, ["Nº INSCRITOS", "Nº CERTIFICADOS"]).head(topn)
            if d.empty:
                st.info("Sem dados para plotar.")
                fig = px.bar(pd.DataFrame(columns=["Nº INSCRITOS","Nº CERTIFICADOS"]), x=["Nº INSCRITOS","Nº CERTIFICADOS"], y=[])
            else:
                fig = px.bar(d, x=["Nº INSCRITOS", "Nº CERTIFICADOS"], y=d.index, orientation="h", barmode="group")

        st.plotly_chart(style_fig(fig), use_container_width=True, key=f"vg_sec_lbl_{modo}_{topn}")
        st.markdown('</div>', unsafe_allow_html=True)

    with colB:
        st.markdown('<div class="panel"><h3>Desempenho por Cargo (Inscritos)</h3>', unsafe_allow_html=True)
        df_rank = repo.cargos_rank()
        if df_rank is None or df_rank.empty:
            st.info("Aba 'CARGOS' vazia ou inválida.")
        else:
            d = nz(df_rank, ["Inscritos"]).head(topn).sort_values("Inscritos")
            if d.empty:
                st.info("Sem dados para o ranking.")
            else:
                fig2 = px.bar(d, x="Inscritos", y=d.index, orientation="h", title=f"Top {topn} Cargos por Inscritos")
                st.plotly_chart(style_fig(fig2), use_container_width=True, key=f"vg_cargo_top_lbl_{topn}")
        st.markdown('</div>', unsafe_allow_html=True)

    # FUNIL
    tot_insc, tot_cert, *_ = repo.get_kpis()
    st.markdown('<div class="panel"><h3>Funil de Conversão</h3>', unsafe_allow_html=True)
    if tot_insc > 0:
        funil_df = pd.DataFrame({"Etapa": ["Inscritos", "Certificados"], "Total": [tot_insc, tot_cert]})
        funil_df = nz(funil_df, ["Total"])
        if funil_df.empty:
            st.info("Sem dados para montar o funil.")
        else:
            fig_funil = px.funnel(funil_df, x="Total", y="Etapa", title=None)
            st.plotly_chart(style_fig(fig_funil, height=360), use_container_width=True, key="vg_funnel")
    else:
        st.info("Sem dados para montar o funil.")
    st.markdown('</div>', unsafe_allow_html=True)
