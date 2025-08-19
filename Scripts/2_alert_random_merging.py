import json
import random
from datetime import datetime

def merge_alerts_randomly():
    # Prompt for input file
    input_file_1 = input("Enter the path to your first jsonl file (e.g. TP_alerts.jsonl): ").strip()
    input_file_2 = input("Enter the path to your second jsonl file (e.g. FP_alerts.jsonl): ").strip()
    # Create unique output files with timestamp information
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"2_alerts_merged_{timestamp}.jsonl"

    # Read and combine entries from both files
    combined = []

    with open(input_file_1, 'r', encoding='utf-8') as in_file_1, open(input_file_2, 'r', encoding='utf-8') as in_file_2:
        # Add file 1 to combined
        for idx, row in enumerate(in_file_1):
            combined.append(json.loads(row))
        # Add file 2 to combined
        for idx, row in enumerate(in_file_2):
            combined.append(json.loads(row))
    
    # Shuffle combined entries
    random.shuffle(combined)

    # Write shuffled order to output
    with open(output_file, 'w', encoding='utf-8') as out_file:
        for row in combined:
            out_file.write(json.dumps(row) + "\n")
    
    print(f"\nMerged alerts have been saved to: {output_file}\n")

# When the script is run directly, execute the function merge_alerts_randomly()
if __name__ == "__main__":
    merge_alerts_randomly()