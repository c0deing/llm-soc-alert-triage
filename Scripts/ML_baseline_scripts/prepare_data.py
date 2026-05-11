"""
prepare_data.py

Loads the merged Wazuh alert JSONL dataset and prepares text + labels
for ML baseline evaluation.

"""

import json
import pandas as pd
from pathlib import Path

INPUT_FILE = Path("2_alerts_preprocessed_merged_20250712_123030.jsonl")
OUTPUT_FILE = Path("prepared_alert_dataset.csv")

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Could not find {INPUT_FILE}. Please place it in the same folder as this script."
    )

def safe_get(d, path, default=""):
    """Safely extract nested dictionary values."""
    current = d
    for key in path:
        if isinstance(current, dict):
            current = current.get(key, default)
        else:
            return default
    return current if current is not None else default

records = []

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for line in f:
        item = json.loads(line)

        label_raw = str(item.get("label", "")).strip().upper()

        # Map labels to numeric values:
        # TP = 1, FP = 0
        if label_raw == "TP":
            label = 1
        elif label_raw == "FP":
            label = 0
        else:
            continue

        src = safe_get(item, ["alert", "_source"], {})

        eventdata = safe_get(src, ["data", "win", "eventdata"], {})
        system = safe_get(src, ["data", "win", "system"], {})
        rule = safe_get(src, ["rule"], {})
        decoder = safe_get(src, ["decoder"], {})
        agent = safe_get(src, ["agent"], {})

        text_parts = [
            item.get("description", ""),
            str(item.get("rule_level", "")),
            item.get("rule_priority", ""),

            safe_get(rule, ["description"], ""),
            str(safe_get(rule, ["id"], "")),
            " ".join(map(str, safe_get(rule, ["groups"], []))) if isinstance(safe_get(rule, ["groups"], []), list) else str(safe_get(rule, ["groups"], "")),

            safe_get(decoder, ["name"], ""),
            safe_get(agent, ["name"], ""),

            safe_get(eventdata, ["commandLine"], ""),
            safe_get(eventdata, ["parentCommandLine"], ""),
            safe_get(eventdata, ["image"], ""),
            safe_get(eventdata, ["parentImage"], ""),
            safe_get(eventdata, ["targetFilename"], ""),
            safe_get(eventdata, ["user"], ""),

            safe_get(system, ["message"], ""),
            safe_get(system, ["severityValue"], ""),
            safe_get(system, ["providerName"], ""),
            safe_get(system, ["channel"], ""),

            safe_get(src, ["full_log"], ""),
            safe_get(src, ["location"], "")
        ]

        text = " ".join([str(x) for x in text_parts if str(x).strip()])

        if text.strip():
            records.append({
                "text": text,
                "label": label,
                "label_name": label_raw
            })

df = pd.DataFrame(records)

if df.empty:
    raise ValueError("No usable records were created. Please check the JSONL structure.")

print("Prepared dataset preview:")
print(df.head())

print("\nLabel distribution:")
print(df["label_name"].value_counts())

print(f"\nNumber of usable records: {len(df)}")

df.to_csv(OUTPUT_FILE, index=False)

print(f"\nPrepared dataset saved to: {OUTPUT_FILE}")
