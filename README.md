# LLM-SOC-Alert-Triage
Artifacts of the dissertation “Possibilities and Limitations of Using Large Language Models (LLMs) for Alert Classification and Prioritisation in Security Operations Centers (SOCs)”. Contains scripts, datasets, results and visualisations. Published to support reproducibility and future research.

## Overview
The project investigates the use of general-purpose LLMs (OpenAI and DeepSeek models) for:
- Classifying security alerts (True Positive vs. False Positive)
- Prioritising alerts (Low / Medium / High / Critical)

The dataset used consists of 178 alerts that were generated in a simulated SOC environment. The setup included:
- Wazuh (SIEM)
- Suricata (IDS integrated with Wazuh)
- Windows Server 2019 (hosting Active Directory)
- Windows 11 Pro (domain-joined client)
- Linux server (running the vulnerable apps DVWA and Mutillidae)
- Kali Linux machine (for carrying out manual attacks)

Alerts were triggered mainly using Atomic Red Team techniques, with additional attacks stemming from the Kali machine. Alerts were exported from Wazuh as JSON for further processing and LLM evaluation.

Evaluation covers classification metrics, prioritisation performance and operational considerations (runtime, cost).

## Repository Structure
- `/scripts/` – Python scripts used for alert preprocessing, classification and prioritisation, evaluation and postprocessing
- `/data/` – dataset (raw and preprocessed JSONL files)
- `/results/` – Evaluation outputs including JSONL outputs, Excel reports and confusion matrix visualisations

## Methodology
0. Raised alerts in Wazuh and gathered them in two JSONL files:
    - `TP_alerts_raw.jsonl` for True Positives (TP)
    - `FP_alerts_raw.jsonl` for False Positives (FP)
2. Preprocessed (and labelled) both files separately using `1_alert_preprocessing.py`
3. Merged both preprocessed JSONL files into one dataset JSONL using `2_alert_random_merging.py`
    - This resulted in `2_alerts_preprocessed_merged_20250712_123030.jsonl` that was used for all models
4. Presented alerts as JSON to LLMs for classification and prioritisation using the OpenAI API python library as can be seen in `3_alert_classification_prioritisation.py`. For DeepSeek models, `3_alert_classification_prioritisation_deepseek-specific.py` was used.
5. Performed postprocessing of results received from LLMs using `4_alert_postprocessing.py`
6. Performed result evaluation using `5_result_evaluation.py`
7. Converted results from JSONL to Excel for manual inspection using `6_jsonl_result_to_excel.py`

### Models evaluated
| Model (Common Name) | Model Version / Snapshot |  
|---|---|
|GPT-4o|gpt-4o-2024-08-06|
|GPT-4.1|gpt-4.1-2025-04-14|
|GPT-4.5 Preview (Deprecated)|gpt-4.5-preview-2025-02-27|
|GPT-4o mini|gpt-4o-mini-2024-07-18|
|GPT-4.1 mini|gpt-4.1-mini-2024-04-14|
|DeepSeek-Chat|DeepSeek-V3-0324|
|DeepSeek-Reasoner|DeepSeek-R1-0528|

### Dataset
178 alerts in total

With regards to Classification:
- True Positives: 104 alerts
- False Positives: 74 alerts

With regards to Prioritisation:
- Low-Priority: 136 alerts
- Medium-Priority: 12 alerts
- High-Priority: 25 alerts
- Critical: 5 alerts

## Results
Key findings:
- LLMs show potential in regards to alert classification i.e. threat detection
  - GPT-4o mini achieved the best recall of 95.19%, yet exhibited a false positive rate of 72.97% 
- All models struggle significantly with prioritisation
  - GPT-4.1 achieved the best macro recall of 34.59% with an accuracy of 49.44% only  

Full results are in the `/results/` folder

## License
This repository is licensed under the [MIT License](LICENSE), allowing reuse and adaptation with proper attribution.

## Citation
If you use this repository in academic work, please cite it as:

Matthias Rieger. (2025). LLM-SOC-Alert-Triage: Artifacts of the research paper “Possibilities and Limitations of Using Large Language Models (LLMs) for Alert Classification and Prioritisation in Security Operations Centers (SOCs)”. GitHub. https://github.com/c0deing/llm-soc-alert-triage

 

