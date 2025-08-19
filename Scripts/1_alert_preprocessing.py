import json
from datetime import datetime

def clean_alert(alert_json):
    # Remove 'highlight' if present
    if "highlight" in alert_json:
        alert_json.pop("highlight", None)

    # Remove 'rule.level' if it exists
    if "_source" in alert_json and "rule" in alert_json["_source"]:
        alert_json["_source"]["rule"].pop("level", None)

    return alert_json

def map_rule_level(level):
    # Map rule level to severity categories
    level = int(level)
    if level >= 15: return "Critical"
    if level >= 12: return "High"
    if level >= 7: return "Medium"
    if level >= 0: return "Low"
    return "MISSING"

def alerts_raw_preprocessing():
    # Prompt for input file
    input_file = input("Enter the path to your jsonl file (e.g. alerts.jsonl): ").strip()
    input_label = input("Enter the label to assign to each row (TP or FP): ").strip()
    # Create unique output files with timestamp information
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"1_{input_label}_alerts_preprocessed_{timestamp}.jsonl"
    # Set for recording alert_ids and duplicate check
    seen_ids = set()
    duplicate_ids = []

    with open(input_file, 'r', encoding='utf-8') as in_file, open(output_file, "w", encoding="utf-8") as out_file:
        for idx, row in enumerate(in_file):
            # Parse json
            alert = json.loads(row.strip())
            # Extract fields
            id = alert.get('_id', 'MISSING')
            # If id has been seen already, skip this row
            if id in seen_ids:
                duplicate_ids.append(id)
                continue
            # Add id to set for duplicate check
            seen_ids.add(id)
            alert_details = alert.get('_source', 'MISSING')
            rule = alert_details.get('rule', 'MISSING')
            rule_level = rule.get('level', -1) # -1 means "missing rule_level"
            rule_priority = map_rule_level(rule_level)
            description = rule.get('description', 'MISSING')
            # Remove unwanted fields from the raw alert to present to LLM
            cleaned_alert = clean_alert(alert)

            # Structure of rows in output file
            entry = {
                "id": id,
                "description": description,
                "label": input_label,
                "rule_level": rule_level,
                "rule_priority": rule_priority,
                "alert": cleaned_alert
            }

            out_file.write(json.dumps(entry) + "\n")

    print(f"\nCleaned alerts saved to: {output_file}\nDuplicate IDs: {duplicate_ids}")

# When the script is run directly, execute the function alerts_raw_preprocessing()
if __name__ == "__main__":
    alerts_raw_preprocessing()
