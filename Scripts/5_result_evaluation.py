import json
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, f1_score, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import os

def map_high_critical(prio):
    # HC = High+Critical
    return "HC" if prio in ["High", "Critical"] else "Other"

def evaluate_from_jsonl():
    input_file = input("Enter the path to your jsonl file (e.g. classified_alerts.jsonl):\n").strip()
    # remove file extension and keep name only
    file_name = os.path.splitext(input_file)[0]
    true_labels = []
    pred_labels = []
    true_priorities = []
    pred_priorities = []

    # Create Excel writer
    excel_path = f'5_{file_name}_evaluation_report.xlsx'
    writer = pd.ExcelWriter(excel_path, engine='xlsxwriter')
    workbook = writer.book

    with open(input_file, "r", encoding="utf-8") as in_file:
        for idx, row in enumerate(in_file):
            alert_row = json.loads(row.strip())

            # Extract ground truth and prediction
            true_label = alert_row["label"].strip().upper()
            pred_label = alert_row["chatgpt_classification"].strip().upper()

            true_priority = alert_row["rule_priority"].strip().capitalize()
            pred_priority = alert_row["chatgpt_priority"].strip().capitalize()

            true_labels.append(true_label)
            pred_labels.append(pred_label)

            true_priorities.append(true_priority)
            pred_priorities.append(pred_priority)
    
    # --- Classification Metrics ---
    print("\nClassification Report (TP vs FP):")
    class_labels = ["FP", "TP"]
    
    class_report = classification_report(true_labels, pred_labels, labels=class_labels, output_dict=True, zero_division=0)
    class_report_df = pd.DataFrame(class_report).transpose()
    print(pd.DataFrame(class_report).transpose().to_string())

    # Confusion matrix
    print("\nConfusion Matrix:")
    cm = confusion_matrix(true_labels, pred_labels, labels=class_labels)
    cm_df = pd.DataFrame(cm, index=class_labels, columns=class_labels)
    print(cm)

    # Extract values from confusion matrix
    tn, fp, fn, tp = cm.ravel()

    # Calculate key rates
    tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    fnr = fn / (tp + fn) if (fp + tn) > 0 else 0
    
    print(f"\nTrue Positive Rate (TPR) = Recall: {tpr:.4f}")
    print(f"False Positive Rate (FPR): {fpr:.4f}")
    print(f"False Negative Rate (FNR): {fnr:.4f}")

    # Create metrics DataFrame
    metrics_data = {
        'Metric': ['TPR', 'FPR', 'FNR'],
        'Value': [tpr, fpr, fnr]
    }
    metrics_df = pd.DataFrame(metrics_data)

    # Write classification data to Excel
    worksheet_class = workbook.add_worksheet('Classification')
    row_pos = 0
    spacing = 3
    # Section 1: Classification Report
    worksheet_class.write(row_pos, 0, "Classification Report")
    class_report_df.to_excel(writer, sheet_name='Classification', startrow=row_pos + 1)
    row_pos += len(class_report_df) + spacing
    # Section 2: Confusion Matrix
    worksheet_class.write(row_pos, 0, "Confusion Matrix")
    cm_df.to_excel(writer, sheet_name='Classification', startrow=row_pos + 1)
    row_pos += len(cm_df) + spacing 
    # Section 3: Key Metrics
    worksheet_class.write(row_pos, 0, "Key Metrics")
    metrics_df.to_excel(writer, sheet_name='Classification', startrow=row_pos + 1, index=False)

    # --- Prioritisation Metrics ---
    print("\nPrioritisation Report (Low/Medium/High/Critical):")

    # Classification report
    priority_labels = ["Critical", "High", "Medium", "Low"]

    priority_report = classification_report(true_priorities, pred_priorities, labels=priority_labels, output_dict=True, zero_division=0)
    priority_report_df = pd.DataFrame(priority_report).transpose()
    print(pd.DataFrame(priority_report).transpose().to_string())

    # Macro F1 Score
    macro_f1 = f1_score(true_priorities, pred_priorities, labels=priority_labels, average='macro', zero_division=0)
    print(f"\nMacro F1 Score: {macro_f1:.4f}")

    # Confusion matrix
    print("\nConfusion Matrix:")
    cm_priority = confusion_matrix(true_priorities, pred_priorities, labels=priority_labels)
    cm_priority_df = pd.DataFrame(cm_priority, index=priority_labels, columns=priority_labels)
    print(cm_priority)

    # Combined class High-Critical = HC calculation
    print("\nHigh+Critical Combined:")
    hc_labels = ["Other", "HC"]
    hc_true = [map_high_critical(prio) for prio in true_priorities]
    hc_pred = [map_high_critical(prio) for prio in pred_priorities]

    hc_report = classification_report(hc_true, hc_pred, labels=hc_labels, output_dict=True, zero_division=0)
    hc_report_df = pd.DataFrame(hc_report).transpose()
    print(pd.DataFrame(hc_report).transpose().to_string())

    cm_hc = confusion_matrix(hc_true, hc_pred, labels=hc_labels)
    cm_hc_df = pd.DataFrame(cm_hc, index=hc_labels, columns=hc_labels)
    print("\nHC Confusion Matrix:")
    print(cm_hc)

    # Extract values from confusion matrix
    tn, fp, fn, tp = cm_hc.ravel()

    # Calculate key rates
    tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    fnr = fn / (tp + fn) if (fp + tn) > 0 else 0
    
    print(f"\nTrue Positive Rate (TPR) = Recall: {tpr:.4f}")
    print(f"False Positive Rate (FPR): {fpr:.4f}")
    print(f"False Negative Rate (FNR): {fnr:.4f}")

    # Create hc metrics DataFrame
    hc_metrics_data = {
        'Metric': ['TPR', 'FPR', 'FNR'],
        'Value': [tpr, fpr, fnr]
    }
    hc_metrics_df = pd.DataFrame(hc_metrics_data)

    # Create prioritisation metrics DataFrame
    priority_metrics_data = {
        'Metric': ["Macro F1 Score"],
        'Value': [macro_f1]
    }
    priority_metrics_df = pd.DataFrame(priority_metrics_data)

    # Write prioritisation data to Excel with headings
    worksheet_prio = workbook.add_worksheet('Prioritisation')
    row_pos = 0
    # Section 1: Prioritisation Report
    worksheet_prio.write(row_pos, 0, "Prioritisation Report")
    priority_report_df.to_excel(writer, sheet_name='Prioritisation', startrow=row_pos + 1)
    row_pos += len(priority_report_df) + spacing
    # Section 2: Confusion Matrix
    worksheet_prio.write(row_pos, 0, "Prioritisation Confusion Matrix")
    cm_priority_df.to_excel(writer, sheet_name='Prioritisation', startrow=row_pos + 1)
    row_pos += len(cm_priority_df) + spacing
    # Section 3: Prioritisation Metrics
    worksheet_prio.write(row_pos, 0, "Prioritisation Metrics")
    priority_metrics_df.to_excel(writer, sheet_name='Prioritisation', startrow=row_pos + 1, index=False)
    row_pos += len(priority_metrics_df) + spacing
    # Section 4: High+Critical Combined Report
    worksheet_prio.write(row_pos, 0, "High+Critical Combined Report")
    hc_report_df.to_excel(writer, sheet_name='Prioritisation', startrow=row_pos + 1)
    row_pos += len(hc_report_df) + spacing
    # Section 5: High+Critical Confusion Matrix
    worksheet_prio.write(row_pos, 0, "High+Critical Confusion Matrix")
    cm_hc_df.to_excel(writer, sheet_name='Prioritisation', startrow=row_pos + 1)
    row_pos += len(cm_hc_df) + spacing
    # Section 6: High+Critical Metrics
    worksheet_prio.write(row_pos, 0, "High+Critical Metrics")
    hc_metrics_df.to_excel(writer, sheet_name='Prioritisation', startrow=row_pos + 1, index=False)

    # Visualise confusion matrices
    # cm classification
    disp = ConfusionMatrixDisplay(cm,display_labels=class_labels)
    disp.plot()
    plt.title('Classification Confusion Matrix')
    plt.savefig(f'5_{file_name}_classification_cm.png', dpi=300)
    print(f"\nSaved confusion matrix visualisations to\n'5_{file_name}_classification_cm.png'")
    # cm prioritisation
    disp = ConfusionMatrixDisplay(cm_priority, display_labels=priority_labels)
    disp.plot()
    plt.title('Prioritisation Confusion Matrix')
    plt.savefig(f'5_{file_name}_prioritisation_cm.png', dpi=300)
    print(f"'5_{file_name}_prioritisation_cm.png'")
    # cm hc combined
    disp = ConfusionMatrixDisplay(cm_hc,display_labels=hc_labels)
    disp.plot()
    plt.title('High+Critical Confusion Matrix')
    plt.savefig(f'5_{file_name}_hc_cm.png', dpi=300)
    print(f"'5_{file_name}_hc_cm.png'")

    # Save Excel file
    writer.close()
    print(f"\nSaved full evaluation report to:\n{excel_path}")

if __name__ == "__main__":
    evaluate_from_jsonl()