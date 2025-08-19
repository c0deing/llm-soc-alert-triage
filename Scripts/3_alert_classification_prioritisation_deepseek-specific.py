from openai import OpenAI
import json
import time
from datetime import datetime

# Configuration
MODEL = "deepseek-reasoner"

def query_chatgpt(alert):
    client = OpenAI(api_key="<api key removed>", base_url="https://api.deepseek.com")
    # Query Deepseek and return json response
    system_prompt = (
        "You are a cybersecurity expert working as a SOC analyst assistant. "
        "Classify the security alert as TP (True Positive) or FP (False Positive) "
        "and assign a Priority: Low, Medium, High or Critical. "
        "Always respond in this exact JSON format:"
        '{"id": "alert_id", "classification": "TP or FP", '
        '"priority": "Low/Medium/High/Critical", "justification": "short explanation"}'
    )
    
    try:
        # Start API timing
        start_time = time.perf_counter()
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(alert)}
            ],
            response_format={
                'type': 'json_object'
            }
        )
        # Calculate API duration
        api_time = time.perf_counter() - start_time
        content = response.choices[0].message.content
        return json.loads(content), api_time
    except Exception as e:
        print(f"Error querying ChatGPT: {e}")
        return None
    
def process_alerts():
    # Start overall timing
    script_start = time.perf_counter()
    api_total_time = 0
    processed_count = 0

    # Prompt for input file
    input_file = input("Enter the path to your jsonl file (e.g. preprocessed_alerts.jsonl): ").strip()
    # Create unique output files with timestamp information
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"3_alerts_classified_prioritised_{timestamp}.jsonl"

    with open(input_file, 'r', encoding='utf-8') as in_file, open(output_file, "w", encoding="utf-8") as out_file:
        for idx, row in enumerate(in_file):
            # Parse json row
            alert_row = json.loads(row.strip())
            processed_count += 1
            # Extract fields
            alert = alert_row.get('alert', 'MISSING')
            id = alert_row.get('id', 'MISSING')
            # Query ChatGPT if response doesn't exist
            if 'chatgpt_response' not in alert_row:
                chatgpt_response, api_time = query_chatgpt(alert)
                api_total_time += api_time
                if chatgpt_response is None:
                    chatgpt_response = {
                        "alert_id": id,
                        "classification": "ERROR",
                        "priority": "ERROR",
                        "justification": "ERROR"
                    }
            
            # Extract ChatGPT fields
            chatgpt_classification = chatgpt_response.get('classification', 'MISSING').strip().upper()
            chatgpt_priority = chatgpt_response.get('priority', 'MISSING').strip().capitalize()
            chatgpt_justification = chatgpt_response.get('justification', 'MISSING')

            # Get ground truth
            label = alert_row.get('label', 'MISSING').upper()
            rule_priority = alert_row.get('rule_priority', 'MISSING')

            # Check for matches
            classification_match = (chatgpt_classification == label)
            priority_match = (chatgpt_priority == rule_priority)

            # Update alert
            alert_row.update({
                'chatgpt_response': chatgpt_response,
                'chatgpt_classification': chatgpt_classification,
                'chatgpt_priority': chatgpt_priority,
                'chatgpt_justification': chatgpt_justification,
                'classification_match': classification_match,
                'priority_match': priority_match
            })

            out_file.write(json.dumps(alert_row) + "\n")
    
    # Calculate final statistics
    script_time = time.perf_counter() - script_start
    
    # Print statistics to console
    print("\n" + "=" * 50)
    print("PROCESSING STATISTICS")
    print("=" * 50)
    print(f"Total alerts processed: {processed_count}")
    print(f"Total script time: {script_time:.2f} seconds")
    print(f"Total API time: {api_total_time:.2f} seconds")
    print(f"Average API time per alert: {api_total_time/processed_count:.4f} seconds")
    print(f"Model used: {MODEL}")
    print("=" * 50)
    print(f"\nAlerts processed by ChatGPT have been saved to: {output_file}")

# When the script is run directly, execute the function process_alerts()
if __name__ == "__main__":
    process_alerts()