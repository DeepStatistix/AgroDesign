import pandas as pd
from importlib.resources import files

_DATASETS = {
    "crd": "crd.csv",
    "rcbd": "rcbd.csv",
    "factorial": "factorial.csv",
    "splitplot": "splitplot.csv",
    "mixed": "mixed.csv",
    "gxe": "gxe.csv",
    "grouped": "grouped.csv",
    "multitrait": "multitrait.csv",
}


def load_dataset(name: str) -> pd.DataFrame:
    """
    Load a built-in AgroDesign tutorial dataset.

    Available:
    crd, rcbd, factorial, splitplot, mixed, gxe, grouped, multitrait
    """

    name = name.lower()

    if name not in _DATASETS:
        available = ", ".join(_DATASETS.keys())
        raise ValueError(f"Unknown dataset '{name}'. Available: {available}")

    path = files("agrodesign.datasets.data").joinpath(_DATASETS[name])
    return pd.read_csv(path)
