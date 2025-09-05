from dataclasses import dataclass
from pathlib import Path
import pandas as pd
import numpy as np

from app.data.readers import load_sheets
from app.domain.filters import clean_secretarias
from app.domain.kpis import get_totais_visao, count_secretarias_unicas


@dataclass
class DataRepository:
    excel_path: Path

    # objetos carregados
    df_dados: pd.DataFrame | None = None
    df_visao: pd.DataFrame | None = None
    df_secretarias_raw: pd.DataFrame | None = None
    df_secretarias: pd.DataFrame | None = None
    df_cargos_raw: pd.DataFrame | None = None
    df_cargos_ev: pd.DataFrame | None = None
    df_cargos_rank: pd.DataFrame | None = None
    cargo_cols: list | None = None

    def load(self):
        (self.df_dados,
         self.df_visao,
         self.df_secretarias_raw,
         self.df_cargos_raw,
         _df_min) = load_sheets(self.excel_path)

        # limpa SECRETARIA-ÓRGÃO
        self.df_secretarias = clean_secretarias(self.df_secretarias_raw)

        # prepara CARGOS
        evento_col = self.df_cargos_raw.columns[0]
        mask_evento = self.df_cargos_raw[evento_col].astype(str).str.contains(
            r"Masterclass|Workshop|Curso", case=False, na=False
        )
        self.df_cargos_ev = self.df_cargos_raw.loc[mask_evento].copy()
        self.df_cargos_ev["Tipo"] = (
            self.df_cargos_ev[evento_col]
            .str.extract(r"(Masterclass|Workshop|Curso)", expand=False)
            .str.title()
            .replace({"Curso": "Curso de IA"})
        )
        self.cargo_cols = [c for c in self.df_cargos_ev.columns if c not in [evento_col, "Tipo"]]
        self.df_cargos_ev[self.cargo_cols] = (
            self.df_cargos_ev[self.cargo_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
        )
        totais_por_cargo = self.df_cargos_ev[self.cargo_cols].sum().sort_values(ascending=False)
        self.df_cargos_rank = (
            pd.DataFrame({"Cargo": totais_por_cargo.index, "Inscritos": totais_por_cargo.values})
            .sort_values("Inscritos", ascending=False).set_index("Cargo")
        )

    # ---- exposed helpers -----------------------------------------------------

    def get_kpis(self, alias: dict | None = None) -> tuple[int, int, float, int]:
        tot_insc, tot_cert = get_totais_visao(self.df_visao)
        taxa_cert = (tot_cert / tot_insc * 100) if tot_insc else 0.0
        sec_atendidas = count_secretarias_unicas(self.df_secretarias, alias=alias)
        return tot_insc, tot_cert, taxa_cert, sec_atendidas

    def secretarias_filtered(self) -> pd.DataFrame:
        """Por enquanto, usa todas as secretarias (filtro oculto)."""
        return self.df_secretarias.copy()

    def cargos_rank(self) -> pd.DataFrame:
        return self.df_cargos_rank.copy()

    def cargos_ev(self) -> pd.DataFrame:
        return self.df_cargos_ev.copy()

    def visao(self) -> pd.DataFrame:
        return self.df_visao.copy()
