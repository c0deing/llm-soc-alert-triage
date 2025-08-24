import json
import re
import unicodedata
import os

def normalize_classification(input_str):
    # Convert to uppercase and remove extra spaces
    clean_str = input_str.strip().upper()
    # Check for TP patterns
    if re.search(r'\b(TP|TRUE\s*POSITIVE)\b', clean_str):
        return "TP"
    # Check for FP patterns
    if re.search(r'\b(FP|FALSE\s*POSITIVE)\b', clean_str):
        return "FP"
    # Return original if no match
    return clean_str

def allowed_priority(priority_str):
    allowed_priorities = ["Low", "Medium", "High", "Critical"]
    # Clean the input string
    clean_str = priority_str.strip().capitalize()
    # Check for exact match first
    if clean_str in allowed_priorities:
        return True
    else:
        return False

def clean_justification(text):
    # Convert to string
    text = str(text)
    # Remove control characters
    text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
    # Remove invalid Unicode characters
    text = ''.join(
        char for char in text 
        if unicodedata.category(char)[0] not in ('C',)
    )
    # Truncate justification text
    MAX_LENGTH = 30000
    if len(text) > MAX_LENGTH:
        text = text[:MAX_LENGTH] + " [TRUNCATED]"
    return text

def alert_postprocesing_from_jsonl():
    input_file = input("Enter the path to your jsonl file (e.g. classified_alerts.jsonl): ").strip()
    # remove file extension and keep name only
    file_name = os.path.splitext(input_file)[0]
    output_file = f"4_{file_name}_postprocessed.jsonl"
    bad_priorities = []

    with open(input_file, 'r', encoding='utf-8') as in_file, open(output_file, "w", encoding="utf-8") as out_file:
        for idx, row in enumerate(in_file):
            alert_row = json.loads(row.strip())
            # Extract fields from json
            chatgpt_classification = alert_row.get('chatgpt_classification', 'MISSING')
            chatgpt_priority = alert_row.get('chatgpt_priority', 'MISSING')
            label = alert_row.get('label', 'MISSING')
            chatgpt_justification = alert_row.get('chatgpt_justification', 'MISSING')
            classification_match = alert_row.get('classification_match', 'MISSING')
            priority_match = alert_row.get('chatgpt_priority', 'MISSING')
            # Check whether false match due to improper formatting
            if classification_match == False:
                # Normalize classification in case gpt returned something like: TRUE POSITIVE (TP) or TP (TRUE POSITIVE) instead of TP only
                chatgpt_classification = normalize_classification(chatgpt_classification)
                # Check again for match
                classification_match = (chatgpt_classification == label)
                # Update alert row
                alert_row.update({
                    'chatgpt_classification': chatgpt_classification,
                    'classification_match': classification_match
                })
            # Check whether false match due to improper formatting
            if priority_match == False:
                # If priority is not one of the allowed ones
                if allowed_priority(chatgpt_priority) == False:
                    # Append the alert id to bad_priorities
                    bad_priorities.append(id)
            # Clean chatgpt_justification string
            chatgpt_justification = clean_justification(chatgpt_justification)
            alert_row.update({
                    'chatgpt_justification': chatgpt_justification
                })
            # Write row to new file
            out_file.write(json.dumps(alert_row) + "\n")

    print(f"\nPost processed alerts have been saved to: {output_file}\nBad Priorities: {bad_priorities}")

if __name__ == "__main__":

    alert_postprocesing_from_jsonl()
