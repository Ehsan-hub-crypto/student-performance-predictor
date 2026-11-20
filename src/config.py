"""Central configuration: paths, app constants and default category thresholds."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

APP_NAME = "EduPredict AI"
# TODO: replace with your own repository URL before publishing.
GITHUB_URL = "https://github.com/your-username/student-performance-predictor"

DATA_PATH = ROOT / "data" / "student_data.csv"
TRAIN_PATH = ROOT / "data" / "train.csv"
TEST_PATH = ROOT / "data" / "test.csv"
MODEL_PATH = ROOT / "models" / "model.pkl"
DB_PATH = ROOT / "data" / "predictions.db"
LOGO_PATH = ROOT / "assets" / "logo.png"

# Category thresholds (minimum predicted score for each band). Configurable in the sidebar.
DEFAULT_THRESHOLDS = {"Excellent": 75.0, "Good": 60.0, "Average": 40.0}
CATEGORIES = ["Excellent", "Good", "Average", "Needs Improvement"]

RANDOM_STATE = 42
TEST_SIZE = 0.2
