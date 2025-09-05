import pandas as pd
import numpy as np

def _find_header_row(df: pd.DataFrame) -> int:
    """Detecta em até 15 primeiras linhas onde está o cabeçalho real."""
    for i in range(min(15, len(df))):
        row_txt = " ".join([str(v).upper() for v in df.iloc[i].tolist()])
        if "SECRETARIA/ÓRGÃO" in row_txt and "INSCRIT" in row_txt:
            return i
    return 0

def _col_like(df: pd.DataFrame, *keywords):
    up = {c: str(c).upper().replace("\xa0", " ") for c in df.columns}
    for c, name in up.items():
        if all(k.upper() in name for k in keywords):
            return c
    return None

def drop_empty_labels(df: pd.DataFrame, col: str) -> pd.DataFrame:
    s = df[col].astype(str)
    mask = s.str.strip().ne("") & ~s.str.lower().isin(["nan", "none", "nat"])
    return df.loc[mask].copy()

def clean_secretarias(df_secretarias_raw: pd.DataFrame) -> pd.DataFrame:
    """Limpa a aba SECRETARIA-ÓRGÃO (cabeçalho dinâmico, remove totais e normaliza números)."""
    df = df_secretarias_raw.copy()
    hdr = _find_header_row(df)
    df = df.iloc[hdr:].reset_index(drop=True)
    df.columns = df.iloc[0]
    df = df.iloc[1:].copy()

    # remover linhas de seções/totais
    mask_meta = df.astype(str).apply(
        lambda s: s.str.upper().str.contains("ATIVIDADE/EVENTO|TOTAL GERAL|^TOTAL$", na=False)
    ).any(axis=1)
    df = df[~mask_meta].dropna(how="all").copy()

    # identificar colunas
    col_ins = _col_like(df, "INSCRIT") or "Nº INSCRITOS"
    col_cer = _col_like(df, "CERTIFIC") or "Nº CERTIFICADOS"
    col_eva = _col_like(df, "EVAS")     or "Nº EVASÃO"

    # normaliza numéricos
    for col in [col_ins, col_cer, col_eva]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # coluna de órgão
    nome_org_col = [c for c in df.columns if "SECRETARIA" in str(c).upper() or "ÓRGÃO" in str(c).upper()][0]
    df[nome_org_col] = df[nome_org_col].astype(str).str.strip()

    # renomeia padrões
    ren = {
        nome_org_col: "SECRETARIA/ÓRGÃO",
        col_ins: "Nº INSCRITOS",
        col_cer: "Nº CERTIFICADOS",
    }
    if col_eva in df.columns:
        ren[col_eva] = "Nº EVASÃO"

    df = df.rename(columns=ren)
    keep = ["SECRETARIA/ÓRGÃO", "Nº INSCRITOS", "Nº CERTIFICADOS"]
    if "Nº EVASÃO" in df.columns:
        keep.append("Nº EVASÃO")
    df = df[keep]

    # remove rótulos vazios
    df = drop_empty_labels(df, "SECRETARIA/ÓRGÃO")
    return df
