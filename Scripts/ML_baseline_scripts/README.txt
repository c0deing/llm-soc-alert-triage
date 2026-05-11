Files
-----
prepare_data.py
    Extracts nested alert text fields and creates prepared_alert_dataset.csv.

run_baselines.py
    Runs Logistic Regression, Random Forest, and Linear SVM using TF-IDF and stratified 5-fold cross-validation.

Required input file
-------------------
2_alerts_preprocessed_merged_20250712_123030.jsonl

How to run
----------
python prepare_data.py
python run_baselines.py

Outputs
-------
prepared_alert_dataset.csv
ml_baseline_results.csv

Reproducibility
---------------
random_state=42 is used for:
- StratifiedKFold
- Logistic Regression
- Random Forest
- Linear SVM
