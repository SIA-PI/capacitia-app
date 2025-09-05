import pandas as pd
import plotly.express as px
import streamlit as st

from app.domain.filters import drop_empty_labels
from app.charts.common import style_fig, nz

TOPN_DEFAULT = 10

def render(repo, topn: int = TOPN_DEFAULT):
    df_f = repo.secretarias_filtered()
    df_f = drop_empty_labels(df_f, "SECRETARIA/ÓRGÃO")

    grp = (
        df_f.groupby('SECRETARIA/ÓRGÃO')[['Nº INSCRITOS','Nº CERTIFICADOS']]
            .sum()
            .reset_index()
    )
    grp = nz(grp, ['Nº INSCRITOS','Nº CERTIFICADOS'])
    grp['Taxa de Certificação (%)'] = (
        grp['Nº CERTIFICADOS'] / grp['Nº INSCRITOS']
    ).replace([pd.NA, float('inf')], 0).fillna(0) * 100

    # Tabela opcional
    show_tbl = st.toggle("Mostrar tabela de secretarias", value=False,
                         help="Ative para visualizar o consolidado; por padrão fica oculto.")
    if show_tbl:
        st.markdown('<div class="panel"><h3>Consolidado por Secretaria/Órgão</h3>', unsafe_allow_html=True)
        st.dataframe(grp.round(2), use_container_width=True, height=min(640, 60 + 28 * min(len(grp), 22)))
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel"><h3>Inscritos X Certificados</h3>', unsafe_allow_html=True)
    cA, cB = st.columns(2)

    with cA:
        top_comp = grp.sort_values('Nº INSCRITOS', ascending=False).head(topn)
        if top_comp.empty:
            st.info("Sem dados para o comparativo.")
        else:
            fig_comp = px.bar(top_comp, x=['Nº INSCRITOS','Nº CERTIFICADOS'], y='SECRETARIA/ÓRGÃO',
                              orientation='h', barmode='group', text_auto=True, title=None)
            fig_comp.update_traces(textposition="outside", cliponaxis=False, textfont_size=12)
            st.plotly_chart(style_fig(fig_comp), use_container_width=True, key=f"sec_comp_{topn}")

    with cB:
        top_taxa = grp[grp['Nº INSCRITOS'] > 0].sort_values('Taxa de Certificação (%)', ascending=False).head(topn)
        top_taxa = nz(top_taxa, ['Taxa de Certificação (%)'])
        if top_taxa.empty:
            st.info("Sem dados para taxa.")
        else:
            fig_taxa = px.bar(top_taxa, x='Taxa de Certificação (%)', y='SECRETARIA/ÓRGÃO',
                              orientation='h', title=f'Top {topn} por Taxa de Certificação',
                              text='Taxa de Certificação (%)')
            fig_taxa.update_traces(texttemplate='%{text:.0f}%', textposition='outside', cliponaxis=False, textfont_size=12)
            fig_taxa.update_xaxes(ticksuffix="%")
            st.plotly_chart(style_fig(fig_taxa), use_container_width=True, key=f"sec_taxa_top_{topn}")

    st.markdown('<div class="panel"><h3>Participação no total de Inscritos</h3>', unsafe_allow_html=True)
    grp_tree = grp.sort_values('Nº INSCRITOS', ascending=False).head(max(topn*2, 20))
    grp_tree = nz(grp_tree, ['Nº INSCRITOS'])
    if grp_tree.empty:
        st.info("Sem dados para o treemap.")
    else:
        treemap = px.treemap(grp_tree, path=['SECRETARIA/ÓRGÃO'], values='Nº INSCRITOS',
                             color='Taxa de Certificação (%)', custom_data=['Taxa de Certificação (%)'],
                             title='Treemap — maiores contribuições')
        treemap.update_traces(texttemplate="<b>%{label}</b><br>%{customdata[0]:.0f}%", textposition="middle center")
        treemap.update_layout(uniformtext_minsize=12, uniformtext_mode='show')
        st.plotly_chart(style_fig(treemap, height=520), use_container_width=True, key="sec_tree")
    st.markdown('</div>', unsafe_allow_html=True)
