import re
import numpy as np
import pandas as pd

def parse_ptbr_number(x):
    """Converte número no formato pt-BR (milhar . e decimal ,) para float. Robusto a símbolos."""
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return np.nan
    s = str(x).strip()
    s = s.replace("\xa0", " ").replace(" ", "")
    s = re.sub(r"[^\d,.\-]", "", s)
    # padrão ptbr: 1.234,56
    if re.match(r"^-?\d{1,3}(\.\d{3})*(,\d+)?$", s):
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except Exception:
        return np.nan
