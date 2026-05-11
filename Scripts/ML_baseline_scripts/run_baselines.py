"""
run_baselines.py

Runs TF-IDF ML baseline models for binary TP/FP classification.
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import StratifiedKFold, cross_validate, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.metrics import confusion_matrix

DATA_FILE = "prepared_alert_dataset.csv"

df = pd.read_csv(DATA_FILE)

if "text" not in df.columns or "label" not in df.columns:
    raise ValueError("prepared_alert_dataset.csv must contain 'text' and 'label' columns.")

df["text"] = df["text"].fillna("").astype(str)
df = df[df["text"].str.strip() != ""]

X = df["text"]
y = df["label"].astype(int)

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "Linear SVM": LinearSVC(random_state=42)
}

rows = []

for name, model in models.items():

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=5000, stop_words=None)),
        ("clf", model)
    ])

    scores = cross_validate(
        pipeline,
        X,
        y,
        cv=cv,
        scoring=["accuracy", "precision", "recall", "f1"]
    )

    y_pred = cross_val_predict(pipeline, X, y, cv=cv)
    tn, fp, fn, tp = confusion_matrix(y, y_pred, labels=[0, 1]).ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0

    row = {
        "Model": name,
        "Accuracy": scores["test_accuracy"].mean(),
        "Precision": scores["test_precision"].mean(),
        "Recall": scores["test_recall"].mean(),
        "F1-score": scores["test_f1"].mean(),
        "FPR": fpr
    }

    rows.append(row)

    print("=" * 60)
    print(name)
    print(f"Accuracy:  {row['Accuracy']:.4f}")
    print(f"Precision: {row['Precision']:.4f}")
    print(f"Recall:    {row['Recall']:.4f}")
    print(f"F1-score:  {row['F1-score']:.4f}")
    print(f"FPR:       {row['FPR']:.4f}")

results_df = pd.DataFrame(rows)
results_df.to_csv("ml_baseline_results.csv", index=False)

print("\nResults saved to ml_baseline_results.csv")
