# extractor_1b.py

import os
import json
import datetime
from heading_utils import extract_headings_and_text
from semantic_utils import rank_sections_by_similarity

# This is the directory where Docker will mount the collection folder.
DATA_DIR = "/app/data"
PDF_DIR = os.path.join(DATA_DIR, "PDFs")
INPUT_FILE = os.path.join(DATA_DIR, "challenge1b_input.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "challenge1b_output.json")

def main():
    """
    Main function to run the analysis pipeline.
    """
    print("--- Starting PDF Analysis ---")

    # 1. Load persona and job from the correct input file
    try:
        with open(INPUT_FILE, "r") as f:
            input_data = json.load(f)
        persona = input_data["persona"]["role"]
        job = input_data["job_to_be_done"]["task"]
        documents_to_process = [doc["filename"] for doc in input_data["documents"]]
        print(f"Successfully loaded persona '{persona}' and task.")
    except Exception as e:
        print(f"Error loading or parsing {INPUT_FILE}: {e}")
        return

    combined_query = f"Persona: {persona}. Task to be done: {job}"

    # 2. Extract sections from all specified PDF documents
    all_sections = []
    print(f"Processing documents: {documents_to_process}")
    for filename in documents_to_process:
        doc_path = os.path.join(PDF_DIR, filename)
        if os.path.exists(doc_path):
            print(f"Extracting sections from {filename}...")
            doc_sections = extract_headings_and_text(doc_path, filename)
            all_sections.extend(doc_sections)
        else:
            print(f"Warning: Document not found at {doc_path}")

    if not all_sections:
        print("No sections were extracted from any documents. Exiting.")
        return

    # 3. Rank all extracted sections based on semantic similarity
    print("Ranking sections based on similarity to the query...")
    ranked_sections = rank_sections_by_similarity(all_sections, combined_query)
    print(f"Ranking complete. Found {len(ranked_sections)} relevant sections.")

    # 4. Construct the final output JSON in the required format
    output_data = {
        "metadata": {
            "input_documents": documents_to_process,
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.datetime.now().isoformat()
        },
        "extracted_sections": [],
        "subsection_analysis": []
    }

    # Take the top 10 most relevant sections
    for i, item in enumerate(ranked_sections[:10]):
        output_data["extracted_sections"].append({
            "document": item["document"],
            "section_title": item["title"],
            "importance_rank": i + 1,
            "page_number": item["page"]
        })
        output_data["subsection_analysis"].append({
            "document": item["document"],
            "refined_text": item["text"], # This now contains the text under the heading
            "page_number": item["page"]
        })

    # 5. Write the final output file
    try:
        with open(OUTPUT_FILE, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"--- Success! Output saved to {OUTPUT_FILE} ---")
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    main()