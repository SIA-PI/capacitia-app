import re
import numpy as np
import pandas as pd
import unicodedata

from app.utils.numbers import parse_ptbr_number


def _col_like(df, *keywords):
    up = {c: str(c).upper().replace("\xa0", " ") for c in df.columns}
    for c, name in up.items():
        if all(k.upper() in name for k in keywords):
            return c
    return None

def _normalize_org(s: str) -> str:
    s = "" if pd.isna(s) else str(s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))  # remove acentos
    s = re.sub(r"\s+", " ", s).strip().upper()
    return s

def get_totais_visao(df_visao: pd.DataFrame) -> tuple[int, int]:
    """Extrai totais a partir da linha 'TOTAL GERAL' na VISÃO ABERTA, com fallbacks robustos."""
    mask_total = df_visao.astype(str).apply(
        lambda s: s.str.contains("TOTAL GERAL", case=False, na=False)
    ).any(axis=1)
    col_ins = _col_like(df_visao, "INSCRIT") or "Nº INSCRITOS"
    col_cer = _col_like(df_visao, "CERTIFIC") or "Nº CERTIFICADOS"

    if mask_total.any():
        row = df_visao.loc[mask_total].iloc[0]

        val_ins = parse_ptbr_number(row.get(col_ins)) if col_ins in df_visao.columns else np.nan
        val_cer = parse_ptbr_number(row.get(col_cer)) if col_cer in df_visao.columns else np.nan

        if pd.isna(val_ins) or pd.isna(val_cer):
            nums = [parse_ptbr_number(v) for v in row.tolist()]
            nums = [n for n in nums if pd.notna(n)]
            if len(nums) >= 2:
                if pd.isna(val_ins): val_ins = nums[-2]
                if pd.isna(val_cer): val_cer = nums[-1]

        if pd.isna(val_ins) or pd.isna(val_cer):
            ins_col = col_ins if col_ins in df_visao.columns else _col_like(df_visao, "INSCRIT")
            cer_col = col_cer if col_cer in df_visao.columns else _col_like(df_visao, "CERTIFIC")
            ins_sum = pd.to_numeric(df_visao[ins_col], errors="coerce").fillna(0).sum() if ins_col else 0
            cer_sum = pd.to_numeric(df_visao[cer_col], errors="coerce").fillna(0).sum() if cer_col else 0
            return int(round(ins_sum)), int(round(cer_sum))

        return int(round(float(val_ins))), int(round(float(val_cer)))

    # sem TOTAL GERAL: soma as colunas
    ins_col = col_ins if col_ins in df_visao.columns else _col_like(df_visao, "INSCRIT")
    cer_col = col_cer if col_cer in df_visao.columns else _col_like(df_visao, "CERTIFIC")
    tot_insc = pd.to_numeric(df_visao[ins_col], errors="coerce").fillna(0).sum() if ins_col else 0
    tot_cert = pd.to_numeric(df_visao[cer_col], errors="coerce").fillna(0).sum() if cer_col else 0
    return int(round(tot_insc)), int(round(tot_cert))

def count_secretarias_unicas(
    df_secretarias_limpa: pd.DataFrame,
    *,
    only_with_inscritos: bool = True,
    drop_genericos: bool = True,
    alias: dict | None = None
) -> int:
    """Conta quantos órgãos distintos existem, com saneamento e aliases opcionais."""
    df = df_secretarias_limpa.copy()

    if only_with_inscritos and "Nº INSCRITOS" in df.columns:
        insc = pd.to_numeric(df["Nº INSCRITOS"], errors="coerce").fillna(0)
        df = df[insc > 0]

    col = "SECRETARIA/ÓRGÃO"
    org = df[col].astype(str).map(_normalize_org)

    invalid = {"", "NAN", "NONE", "NAT"}
    if drop_genericos:
        invalid |= {"ORGAO EXTERNO", "ÓRGÃO EXTERNO", "ORGAO  EXTERNO"}

    org = org[~org.isin(invalid)]
    if alias:
        org = org.replace({k.upper(): v.upper() for k, v in alias.items()})
    return int(org.nunique())

def fmt_int_br(n: int) -> str:
    return str(f"{int(n):,}").replace(",", ".")
