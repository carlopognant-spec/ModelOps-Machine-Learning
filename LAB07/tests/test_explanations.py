import numpy as np
import pytest

from LAB07.explain_case import normalize_shap, select_cases


def test_old_and_new_shap_class_shapes():
    old = [np.array([[1, 2, 3, 4]]), np.array([[-1, -2, -3, -4]])]
    new = np.stack(old, axis=-1)
    for values in (old, new):
        contributions, base = normalize_shap(values, [0.3, 0.7], 1, 4)
        np.testing.assert_array_equal(contributions, [-1, -2, -3, -4])
        assert base == 0.7


def test_unknown_shape_fails_explicitly():
    with pytest.raises(ValueError, match="Formato"):
        normalize_shap(np.zeros((2, 7)), [0.5, 0.5], 1, 4)


def test_errors_first_and_correct_suspicious_cases_separate():
    pred, real = np.array([0, 1, 1, 0]), np.array([1, 1, 1, 0])
    proba = np.array([[0.9, 0.1], [0.4, 0.6], [0.3, 0.7], [0.8, 0.2]])
    assert select_cases(pred, real, proba) == [0, 1, 2]
