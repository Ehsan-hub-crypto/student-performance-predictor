# 🎓 EduPredict AI — Student Performance Predictor

A Streamlit web app that predicts a student's score from **study hours, attendance, previous marks, assignment completion and sleep**, using a real scikit-learn model (Random Forest Regressor, compared against Linear Regression). Black, gold and white design; SQLite prediction history; analytics dashboard.

> ⚠️ **Read this first:** the bundled dataset (`data/student_data.csv`) is **synthetic** — generated from a hand-written formula plus noise (see `data/data_card.json`). It contains no real students. The metrics below show how well the model learned that synthetic data, **not** real-world accuracy. Predictions are estimates, not guaranteed outcomes.

## Screenshots
Add your own after running the app (create `docs/` and drop images in):

| Home | Predict | Analytics |
|---|---|---|
| `docs/home.png` | `docs/results.png` | `docs/analytics.png` |

## Features
- Home, Predict, Analytics and About pages with responsive navigation and a "Predict Now" button
- Beginner-friendly form (4 sliders + number input) with descriptions, tooltips and full validation
- Real model inference — no hard-coded results; a clear setup message if the model is missing
- Result dashboard: score /100, category, input charts, rule-based recommendations
- Recommendations labelled **Research-backed** (with source) or **General**
- Configurable category thresholds (sidebar); categories are indicative only
- Warning when an input lies outside the range the model learned from
- Analytics: totals, average, category distribution, study/attendance vs predicted score, history
- History in SQLite: save, view dates, compare 2–4 predictions, delete one or all
- Privacy: no names or emails; data stays in a local file (`data/predictions.db`)

## Tech stack
Python · Streamlit · Pandas · NumPy · scikit-learn · Joblib · Plotly · SQLite · Pytest

## Installation
```bash
git clone https://github.com/your-username/student-performance-predictor.git
cd student-performance-predictor
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m src.train          # optional: model.pkl is already included
streamlit run app.py
```
Update `GITHUB_URL` in `src/config.py` to your repository link.

## Usage
1. Open **Predict Performance**, fill the five inputs, press **Predict My Performance**.
2. Read the score, category, charts and tips. Press **Save this prediction** to keep it.
3. Open **Analytics** to see trends, compare saved predictions or delete records.
4. Change category thresholds in the sidebar if your institution grades differently.

To use real data, replace `data/student_data.csv` with a CSV that has columns `study_hours, attendance, previous_marks, assignment_completion, sleep_hours, final_score`, then run `python -m src.train`.

## Project architecture
```
app.py                    Streamlit entry point, navigation and pages
src/config.py             Paths, constants, default thresholds
src/preprocess.py         Validation, cleaning, train/test split
src/generate_data.py      Synthetic data generator (only used if no CSV exists)
src/train.py              Trains RF + Linear Regression, evaluates, saves model.pkl + metrics.json
src/predict.py            Load model, predict, categorise, recommendations
src/database.py           SQLite history (save / list / delete)
components/               sidebar.py, prediction_form.py, results.py, charts.py, styles.py
data/                     student_data.csv, train.csv, test.csv (kept separate), data_card.json
models/                   model.pkl, metrics.json
tests/test_model.py       14 tests (validation, split, prediction, DB, categories)
```
Workflow: Student data → preprocessing → Random Forest → score → category & insights.

## Model evaluation
Evaluated on a 20 % held-out test set (400 rows) never used for training; 1,600 rows used for training.

| Model | MAE ↓ | R² ↑ |
|---|---|---|
| **Random Forest (used)** | 3.70 | 0.864 |
| Linear Regression | 4.21 | 0.794 |

Re-running `python -m src.train` regenerates these numbers and `models/metrics.json`.

## Testing
```bash
python -m pytest
```

## Limitations
- Trained on **synthetic** data: learned relationships are assumptions, not research findings.
- Only five inputs; ignores subject difficulty, teaching quality, health, motivation, etc.
- Less reliable outside the input ranges seen in training.
- Recommendations are hand-written rules, not model output; only those marked Research-backed cite a source.
- Not an official assessment; do not use for decisions about real students.

## License
MIT — see [LICENSE](LICENSE).
