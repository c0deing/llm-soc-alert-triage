import json
import pandas as pd
import os

# Convert enriched JSONL to formatted Excel file
def jsonl_to_excel():
    input_jsonl = input("Enter the path to your jsonl file (e.g. classified_alerts.jsonl): ").strip()
    # Convert enriched JSONL to formatted Excel file
    # Give the xlsx file the same name for easier identification
    # Get the filename without extension
    file_name = os.path.splitext(input_jsonl)[0]
    output_xlsx = f"6_{file_name}.xlsx"
    
    # Collect data for Excel
    excel_data = []
    
    with open(input_jsonl, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                alert = json.loads(line)
                
                # Extract key fields
                row = {
                    "ID": alert.get('id', ''),
                    "Description": alert.get('description', ''),
                    "True Label": alert.get('label', ''),
                    "Rule Level": alert.get('rule_level', ''),
                    "Rule Priority": alert.get('rule_priority', ''),
                    "ChatGPT Classification": alert.get('chatgpt_classification', 'MISSING'),
                    "Classification Match": alert.get('classification_match', False),
                    "ChatGPT Priority": alert.get('chatgpt_priority', 'MISSING'),
                    "Priority Match": alert.get('priority_match', False),
                    "Justification": alert.get('chatgpt_justification', '')
                }
                
                excel_data.append(row)
            except json.JSONDecodeError:
                print(f"Skipping malformed line: {line[:100]}...")
    
    # Create DataFrame
    df = pd.DataFrame(excel_data)
    
    # Reorder columns for logical flow
    column_order = [
        'ID', 'Description', 'True Label', 'ChatGPT Classification', 'Classification Match', 
        'Rule Level', 'Rule Priority','ChatGPT Priority', 'Priority Match', 
        'Justification'
    ]
    df = df[column_order]
    
    # Save to Excel
    df.to_excel(output_xlsx, index=False)
    print(f"Excel saved to {output_xlsx}")

if __name__ == "__main__":
    jsonl_to_excel()