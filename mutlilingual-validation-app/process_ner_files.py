import json
import os

# Define paths
base_path = "/Users/fadyghatas/Downloads/multilingual_ner/final/"
output_folder = os.path.join(base_path, "output")

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Read test.json (groundtruth) - JSONL format
groundtruth = []
with open(os.path.join(base_path, "test.json")) as f:
    for line in f:
        groundtruth.append(json.loads(line))

print(f"Loaded {len(groundtruth)} groundtruth entries")

# Read predictions_bilora_from_spanish_directly.json - JSON array format
# Structure: {text, spanish, ners, tokens, mappings}
with open(os.path.join(base_path, "predictions_bilora_from_spanish_directly.json")) as f:
    spanish_directly = json.load(f)
print(f"Loaded {len(spanish_directly)} spanish_directly entries")

# Read predictions_bilora_from_llama_translated.json - JSON array format  
# Structure: {ners, original, back-translated, mappings}
with open(os.path.join(base_path, "predictions_bilora_from_llama_translated.json")) as f:
    llama_translated = json.load(f)
print(f"Loaded {len(llama_translated)} llama_translated entries")

# Read bable_ner_extracted_test.json - JSONL format
# Structure: {text, ner_tags, ner_results}
bable_ner = []
with open(os.path.join(base_path, "bable_ner_extracted_test.json")) as f:
    for line in f:
        bable_ner.append(json.loads(line))
print(f"Loaded {len(bable_ner)} bable_ner entries")

# Process and combine all data
combined_results = []

for i in range(len(groundtruth)):
    text = groundtruth[i]["text"]
    groundtruth_labels = groundtruth[i]["labels"]
    
    # Add extracted text to groundtruth labels
    updated_labels = []
    for label in groundtruth_labels:
        if len(label) >= 3:
            start = label[0]
            end = label[1]
            entity_type = label[2]
            extracted_text = text[start:end]
            updated_label = [start, end, entity_type, extracted_text]
            updated_labels.append(updated_label)
        else:
            updated_labels.append(label)
    
    entry = {
        "index": i,
        "id": groundtruth[i].get("id", f"entry_{i}"),
        "text": text,
        "groundtruth_labels": updated_labels,
    }
    
    # Add spanish_directly predictions if available (with mappings)
    if i < len(spanish_directly):
        entry["spanish_directly"] = {
            "spanish_text": spanish_directly[i].get("spanish", ""),
            "tokens": spanish_directly[i].get("tokens", []),
            "ners": spanish_directly[i].get("ners", []),
            "mappings": spanish_directly[i].get("mappings", [])
        }
    
    # Add llama_translated predictions if available (with mappings)
    if i < len(llama_translated):
        entry["llama_translated"] = {
            "original": llama_translated[i].get("original", ""),
            "back_translated": llama_translated[i].get("back-translated", ""),
            "ners": llama_translated[i].get("ners", []),
            "mappings": llama_translated[i].get("mappings", [])
        }
    
    # Add bable NER predictions if available
    if i < len(bable_ner):
        entry["bable_ner"] = {
            "text": bable_ner[i].get("text", ""),
            "ner_tags": bable_ner[i].get("ner_tags", []),
            "ner_results": bable_ner[i].get("ner_results", [])
        }
    
    combined_results.append(entry)

# Save combined results with text to output folder
output_path = os.path.join(output_folder, "combined_ner_results_with_text.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(combined_results, f, indent=2, ensure_ascii=False)
print(f"\nSaved combined results to {output_path}")

# Print a sample to verify
print("\n=== Sample from first entry ===")
if combined_results and combined_results[0].get("groundtruth_labels"):
    print(f"ID: {combined_results[0].get('id', 'N/A')}")
    print("First 3 groundtruth_labels with extracted text:")
    for label in combined_results[0]["groundtruth_labels"][:3]:
        print(f"  Start: {label[0]}, End: {label[1]}, Type: {label[2]}, Text: '{label[3]}'")
    
    print("\nSpanish directly mappings sample (first 5):")
    if combined_results[0].get("spanish_directly", {}).get("mappings"):
        print(f"  {combined_results[0]['spanish_directly']['mappings'][:5]}")
    
    print("\nLlama translated mappings sample (first 5):")
    if combined_results[0].get("llama_translated", {}).get("mappings"):
        print(f"  {combined_results[0]['llama_translated']['mappings'][:5]}")

print("\n=== Processing Complete ===")
print(f"Output saved to: {output_folder}")
