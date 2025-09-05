import re
import pandas as pd
import plotly.express as px
import streamlit as st

from app.charts.common import style_fig, nz

TOPN_DEFAULT = 10

def render(repo, topn: int = TOPN_DEFAULT):
    ev = repo.visao()
    if ev is None or ev.empty:
        st.info("Aba 'VISÃO ABERTA' vazia ou inválida.")
        return

    # numéricos
    ev["Nº INSCRITOS"] = pd.to_numeric(ev["Nº INSCRITOS"], errors="coerce")
    ev["Nº CERTIFICADOS"] = pd.to_numeric(ev["Nº CERTIFICADOS"], errors="coerce")
    ev = nz(ev, ["Nº INSCRITOS", "Nº CERTIFICADOS"])

    # tipo e métricas
    ev["Tipo"] = (
        ev["EVENTO"].astype(str)
        .str.extract(r"(Masterclass|Workshop|Curso)", expand=False)
        .str.title()
        .replace({"Curso": "Curso de IA"})
    ).fillna("Outro")
    ev["Taxa de Certificação (%)"] = (
        ev["Nº CERTIFICADOS"] / ev["Nº INSCRITOS"]
    ).replace([pd.NA, float("inf")], 0).fillna(0) * 100
    ev["Evasão (Nº)"] = (ev["Nº INSCRITOS"] - ev["Nº CERTIFICADOS"]).clip(lower=0)

    # Tabela opcional
    show_tbl = st.toggle("Mostrar tabela de eventos", value=False,
                         help="Ative para visualizar a planilha; por padrão fica oculta.")
    if show_tbl:
        cols_evento = [c for c in ["Nº","EVENTO","Tipo","Nº INSCRITOS","Nº CERTIFICADOS","Evasão (Nº)","Taxa de Certificação (%)"] if c in ev.columns]
        st.markdown('<div class="panel"><h3>Eventos (filtrados)</h3>', unsafe_allow_html=True)
        st.dataframe(ev[cols_evento].reset_index(drop=True), use_container_width=True, height=min(640, 60 + 28 * min(len(ev), 22)))
        st.markdown('</div>', unsafe_allow_html=True)

    # Donut por tipo + Box
    by_tipo = ev.groupby("Tipo")[["Nº INSCRITOS","Nº CERTIFICADOS"]].sum()
    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        if not by_tipo.empty:
            pie = px.pie(by_tipo.reset_index(), values="Nº INSCRITOS", names="Tipo", hole=0.55)
            pie.update_layout(legend=dict(orientation="v", y=0.5, yanchor="middle", x=1.02))
            st.plotly_chart(style_fig(pie, height=460), use_container_width=True, key=f"ev_pie_{len(by_tipo)}")
        else:
            st.info("Sem dados para o donut.")

    with col_right:
        if not ev.empty:
            box = px.box(ev, x="Tipo", y="Taxa de Certificação (%)", title="Taxa de Certificação — distribuição por tipo")
            box.update_yaxes(ticksuffix="%")
            st.plotly_chart(style_fig(box, height=460), use_container_width=True, key="ev_box")
        else:
            st.info("Sem dados para o boxplot.")

    # Barras por tipo
    if not by_tipo.empty:
        st.markdown('<div class="panel"><h3>Totais por tipo (Inscritos x Certificados)</h3>', unsafe_allow_html=True)
        by_tipo2 = by_tipo.reset_index().melt(
            id_vars="Tipo", value_vars=["Nº INSCRITOS","Nº CERTIFICADOS"],
            var_name="Métrica", value_name="Total"
        )
        by_tipo2 = nz(by_tipo2, ["Total"])
        if by_tipo2.empty:
            st.info("Sem dados para barras por tipo.")
        else:
            bar_tipo = px.bar(by_tipo2, x="Tipo", y="Total", color="Métrica", barmode="group", title=None)
            maxy = max(1, by_tipo2["Total"].max())
            bar_tipo.update_yaxes(range=[0, maxy * 1.15])
            bar_tipo.update_traces(texttemplate="%{y}", textposition="outside", cliponaxis=False)
            st.plotly_chart(style_fig(bar_tipo, height=420), use_container_width=True, key="ev_bar_tipo")
        st.markdown('</div>', unsafe_allow_html=True)

    # Treemap por evento (com rótulo curto)
    if not ev.empty:
        st.markdown('<div class="panel"><h3>Treemap — participação por evento</h3>', unsafe_allow_html=True)

        def rotulo_curto(evento: str, tipo: str) -> str:
            s = str(evento)
            base = s.split(":", 1)[0].strip() or tipo
            m = re.search(r"(\d+)\s*[ºª]?\s*(Masterclass|Workshop|Curso(?:\s+de\s+IA)?)", base, flags=re.I)
            if m:
                num = m.group(1)
                kind = m.group(2)
                kind = re.sub(r"(?i)^curso(?:\s+de\s+ia)?$", "Curso de IA", kind).title()
                return f"{num}° {kind}"
            return " ".join(base.split()[:4])

        ev_tmp = ev.copy()
        ev_tmp = nz(ev_tmp, ["Nº INSCRITOS"])
        if ev_tmp.empty:
            st.info("Sem dados para o treemap.")
        else:
            ev_tmp["EVENTO_LABEL"] = ev_tmp.apply(lambda r: rotulo_curto(r["EVENTO"], r["Tipo"]), axis=1)
            col_tm, col_desc = st.columns([4, 1.7], gap="large")
            with col_tm:
                tmap = px.treemap(
                    ev_tmp.sort_values("Nº INSCRITOS", ascending=False).head(max(topn*2, 20)),
                    path=["Tipo", "EVENTO_LABEL"], values="Nº INSCRITOS", title=None
                )
                tmap.update_traces(
                    textinfo="label+text",
                    texttemplate="%{label}<br>%{percentRoot:.1%}",
                    textposition="middle center",
                    hovertemplate="<b>%{label}</b><br>Inscritos: %{value}<br>Participação: %{percentRoot:.1%}<extra></extra>",
                )
                st.plotly_chart(style_fig(tmap, height=520), use_container_width=True, key="ev_treemap_labels_pct")
            with col_desc:
                st.markdown("""
                <div class="panel">
                <h3>O que é essa porcentagem?</h3>
                <p>É a <b>participação no total de inscritos</b> considerando todos os filtros atuais.</p>
                <ul>
                    <li><b>Tipo</b> (Curso de IA, Masterclass, Workshop): % do total para cada tipo.</li>
                    <li><b>Evento</b> (ex.: <i>11° Curso</i>): % daquele evento no total.</li>
                </ul>
                <p>Passe o mouse para ver <b>inscritos absolutos</b> e a mesma participação (%).</p>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
