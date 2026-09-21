import csv

from data_loader import DATA_PATH, leggi_csv

EXPECTED_COLUMNS = {"f1", "f2", "label"}


def test_dataset_has_expected_columns_and_rows():
    with DATA_PATH.open(newline="", encoding="utf-8-sig") as file_csv:
        reader = csv.DictReader(file_csv)
        assert set(reader.fieldnames or []) == EXPECTED_COLUMNS
        righe = list(reader)

    assert righe
    assert all(riga["label"] not in (None, "") for riga in righe)


def test_dataset_values_are_convertible():
    righe = leggi_csv(DATA_PATH, tipi={"f1": float, "f2": float, "label": int})
    assert all(riga["label"] in (0, 1) for riga in righe)
