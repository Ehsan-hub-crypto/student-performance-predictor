"""Tests for validation, training, prediction, categories and the SQLite history."""
import numpy as np
import pandas as pd
import pytest

from src import database
from src.predict import ModelUnavailableError, categorize, load_bundle, predict_score, recommendations
from src.preprocess import FEATURES, ValidationError, validate_input
from src.train import train

GOOD = dict(study_hours=5, attendance=85, previous_marks=70, assignment_completion=80, sleep_hours=7.5)


@pytest.fixture(scope="module")
def bundle(tmp_path_factory):
    d = tmp_path_factory.mktemp("m")
    from src.config import DATA_PATH
    return train(DATA_PATH, d / "model.pkl", d / "train.csv", d / "test.csv"), d


def test_validation_accepts_good_input():
    assert validate_input(GOOD)["attendance"] == 85.0


@pytest.mark.parametrize("field,value", [("attendance", 120), ("study_hours", -1), ("sleep_hours", "abc"),
                                         ("previous_marks", None), ("attendance", float("nan"))])
def test_validation_rejects_bad_input(field, value):
    with pytest.raises(ValidationError):
        validate_input({**GOOD, field: value})


def test_validation_reports_missing_fields():
    with pytest.raises(ValidationError) as e:
        validate_input({})
    assert len(e.value.errors) == len(FEATURES)


def test_train_test_are_disjoint_and_metrics_sane(bundle):
    b, d = bundle
    tr, te = pd.read_csv(d / "train.csv"), pd.read_csv(d / "test.csv")
    assert len(tr) + len(te) == b["n_train"] + b["n_test"]
    assert not set(map(tuple, tr.values)) & set(map(tuple, te.values))
    rf = b["metrics"]["Random Forest"]
    assert rf["mae"] < 10 and rf["r2"] > 0.5


def test_prediction_in_range_and_responds_to_inputs(bundle):
    b, _ = bundle
    low = predict_score({**GOOD, "previous_marks": 30, "study_hours": 1}, b)["score"]
    high = predict_score({**GOOD, "previous_marks": 90, "study_hours": 8}, b)["score"]
    assert 0 <= low < high <= 100


def test_out_of_range_warning(bundle):
    b, _ = bundle
    assert predict_score({**GOOD, "study_hours": 12}, b)["warnings"]


def test_missing_model_raises(tmp_path):
    with pytest.raises(ModelUnavailableError):
        load_bundle(tmp_path / "nope.pkl")


def test_categories_and_custom_thresholds():
    assert categorize(80) == "Excellent" and categorize(65) == "Good"
    assert categorize(45) == "Average" and categorize(10) == "Needs Improvement"
    assert categorize(65, {"Excellent": 90, "Good": 70, "Average": 50}) == "Average"


def test_recommendations_react_to_input():
    titles = [r["title"] for r in recommendations({**GOOD, "attendance": 50, "sleep_hours": 4})]
    assert "Improve attendance" in titles and "Maintain a healthy sleep schedule" in titles


def test_database_crud(tmp_path):
    db = tmp_path / "t.db"
    assert database.get_predictions(db).empty
    i = database.save_prediction(GOOD, 71.2, "Good", db)
    database.save_prediction(GOOD, 50.0, "Average", db)
    df = database.get_predictions(db)
    assert len(df) == 2 and np.isclose(df["predicted_score"].mean(), 60.6)
    database.delete_prediction(i, db)
    assert len(database.get_predictions(db)) == 1
    database.delete_all(db)
    assert database.get_predictions(db).empty
