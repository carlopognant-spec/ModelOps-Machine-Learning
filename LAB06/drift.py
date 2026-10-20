"""PSI con bin di riferimento e smoothing normalizzato."""
from dataclasses import dataclass

import numpy as np


def finite_vector(values):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or not len(values) or not np.isfinite(values).all():
        raise ValueError("Servono vettori non vuoti di numeri finiti")
    return values


def reference_edges(reference, bins=10):
    values = finite_vector(reference)
    if bins < 2:
        raise ValueError("Servono almeno 2 bin")
    internal = np.unique(np.quantile(values, np.linspace(0, 1, bins + 1)[1:-1]))
    return np.r_[-np.inf, internal, np.inf]


def psi(reference, current, edges=None, smoothing=0.5):
    ref, cur = finite_vector(reference), finite_vector(current)
    edges = reference_edges(ref) if edges is None else np.asarray(edges, dtype=float)
    if smoothing <= 0 or not np.isfinite(smoothing):
        raise ValueError("Smoothing positivo finito obbligatorio")
    if len(edges) < 3 or not np.all(np.diff(edges) > 0) or edges[0] != -np.inf or edges[-1] != np.inf:
        raise ValueError("Bin crescenti con estremi infiniti obbligatori")
    ref_count = np.histogram(ref, bins=edges)[0]
    cur_count = np.histogram(cur, bins=edges)[0]
    p = (ref_count + smoothing) / (len(ref) + smoothing * len(ref_count))
    q = (cur_count + smoothing) / (len(cur) + smoothing * len(cur_count))
    return float(np.sum((q - p) * np.log(q / p)))


@dataclass
class AlertState:
    threshold: float
    persistence: int = 2
    consecutive: int = 0

    def __post_init__(self):
        if not np.isfinite(self.threshold) or self.threshold < 0:
            raise ValueError("Soglia finita non negativa obbligatoria")
        if type(self.persistence) is not int or self.persistence < 1:
            raise ValueError("Persistenza intera positiva obbligatoria")

    def update(self, score):
        if not np.isfinite(score) or score < 0:
            raise ValueError("Drift score non valido")
        if score > self.threshold:
            self.consecutive += 1
            return "ALERT" if self.consecutive >= self.persistence else "ATTENZIONE"
        self.consecutive = 0
        return "SOTTO SOGLIA"
