import math

import numpy as np
import pytest

from LAB06.drift import AlertState, psi, reference_edges


def test_same_distribution_zero():
    assert psi([1, 2, 3, 4], [1, 2, 3, 4]) == pytest.approx(0)


def test_known_psi_with_smoothing():
    # Due bin: p=(2.5/5,2.5/5), q=(1.5/5,3.5/5).
    expected = (0.3 - 0.5) * math.log(0.3 / 0.5) + (0.7 - 0.5) * math.log(0.7 / 0.5)
    assert psi([0, 0, 2, 2], [0, 2, 2, 2], [-np.inf, 1, np.inf]) == pytest.approx(expected)


def test_zero_bins_and_outliers_are_finite():
    reference = np.arange(100)
    assert np.isfinite(psi(reference, [10000] * 100))
    assert psi(reference, [10000] * 100) > 0.1


def test_no_significant_drift_and_shift():
    reference = np.tile(np.arange(100), 10)
    edges = reference_edges(reference)
    assert psi(reference, reference[::-1], edges) < 0.1
    assert psi(reference, reference + 200, edges) > 0.1


def test_attention_persistence_and_reset():
    state = AlertState(0.1)
    assert state.update(0.05) == "SOTTO SOGLIA"
    assert state.update(0.2) == "ATTENZIONE"
    assert state.update(0.3) == "ALERT"
    assert state.update(0.1) == "SOTTO SOGLIA"
    assert state.consecutive == 0
    assert state.update(0.2) == "ATTENZIONE"


def test_constant_reference_and_invalid_data():
    assert psi([5] * 20, [5] * 20) == pytest.approx(0)
    with pytest.raises(ValueError):
        psi([], [1])
    with pytest.raises(ValueError):
        psi([1], [np.nan])
