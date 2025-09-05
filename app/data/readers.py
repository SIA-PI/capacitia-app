from pathlib import Path
import pandas as pd

def load_sheets(path: Path):
    """Carrega as abas necessárias do Excel. Não faz limpeza aqui."""
    xls = pd.ExcelFile(path)
    df_dados        = pd.read_excel(xls, "DADOS", header=6)
    df_visao        = pd.read_excel(xls, "VISÃO ABERTA", header=6)
    df_secretarias  = pd.read_excel(xls, "SECRETARIA-ÓRGÃO", header=None)  # header dinâmico
    df_cargos_raw   = pd.read_excel(xls, "CARGOS", header=2)
    try:
        df_min      = pd.read_excel(xls, "MINISTRANTECARGA HORÁRIA", header=1)
    except Exception:
        df_min      = None
    return df_dados, df_visao, df_secretarias, df_cargos_raw, df_min
