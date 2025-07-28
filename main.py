# main.py

import os
import json
import fitz  # PyMuPDF
from llama_cpp import Llama
import re  # Import the regular expression module
import datetime # Import the datetime module for timestamps

# --- Configuration ---
DATA_DIR = "/app/data"
MODEL_PATH = "/app/model/qwen1_5-1_8b-chat-q3_k_m.gguf"
PDF_DIR = os.path.join(DATA_DIR, "PDFs")
INPUT_FILE = os.path.join(DATA_DIR, "challenge1b_input.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "challenge1b_output.json")

# --- ONE-SHOT EXAMPLE ---
# Providing an example of the final output dramatically improves model accuracy.
EXAMPLE_OUTPUT = """
{
  "metadata": {
    "input_documents": [
      "South of France - Cities.pdf",
      "South of France - Cuisine.pdf"
    ],
    "persona": "Travel Planner",
    "job_to_be_done": "Plan a trip of 4 days for a group of 10 college friends.",
    "processing_timestamp": "2025-07-27T10:30:00.000000"
  },
  "extracted_sections": [
    {
      "document": "South of France - Things to Do.pdf",
      "section_title": "Nightlife and Entertainment",
      "importance_rank": 1,
      "page_number": 11
    },
    {
      "document": "South of France - Restaurants and Hotels.pdf",
      "section_title": "Budget-Friendly Restaurants",
      "importance_rank": 2,
      "page_number": 2
    }
  ],
  "subsection_analysis": [
    {
      "document": "South of France - Things to Do.pdf",
      "refined_text": "The South of France offers a vibrant nightlife scene... Bars and Lounges... Nightclubs...",
      "page_number": 11
    },
    {
      "document": "South of France - Restaurants and Hotels.pdf",
      "refined_text": "Chez Pipo (Nice): Famous for its socca... La Merenda (Nice): A small, cozy restaurant...",
      "page_number": 2
    }
  ]
}
"""


# Initialize the Local LLM
try:
    print(f"Loading model from {MODEL_PATH}...")
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=4096,
        n_gpu_layers=0,
        verbose=False
    )
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading local LLM model: {e}")
    exit(1)

# --- Helper Functions ---

def extract_text_from_pdfs(pdf_filenames):
    """Extracts text content from a list of PDF files."""
    documents_content = []
    print(f"Starting PDF extraction for: {pdf_filenames}")
    for filename in pdf_filenames:
        doc_path = os.path.join(PDF_DIR, filename)
        if not os.path.exists(doc_path):
            print(f"Warning: PDF file not found at {doc_path}")
            continue
        try:
            doc = fitz.open(doc_path)
            full_text = " ".join([page.get_text("text") for page in doc])
            documents_content.append({"filename": filename, "text": full_text})
            print(f"Successfully extracted text from {filename}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    return documents_content

def llm_call(messages):
    """A centralized function to call the LLM with robust JSON parsing."""
    try:
        response = llm.create_chat_completion(
            messages=messages,
            temperature=0.05, # Lower temperature for more predictable, structured output
        )
        content = response['choices'][0]['message']['content']
        
        json_match = re.search(r'(\{.*\})|(\[.*\])', content, re.DOTALL)
        
        if json_match is None:
            raise ValueError("No valid JSON object or list found in the LLM's response.")
            
        json_string = json_match.group(0)
        return json.loads(json_string)
        
    except Exception as e:
        print(f"LLM call failed: {e}")
        if 'content' in locals():
            print("Raw LLM output:", content)
        return None


def map_document_to_sections(document, persona, task):
    """MAP STEP: Processes a single document to extract relevant sections."""
    print(f"Mapping document: {document['filename']}...")
    
    truncated_text = document['text'][:12000]

    prompt_content = f"""
    Based on the user persona and task, extract relevant sections from the document text.

    **Persona:** {persona['role']}
    **Task:** {task['task']}
    **Document Text:**
    ---
    {truncated_text}
    ---

    Return a JSON list of objects. Each object MUST contain "section_title", "page_number" (integer), and "refined_text" (a concise summary). If nothing is relevant, return an empty list [].
    """
    
    messages = [
        {"role": "system", "content": "You are an AI assistant that extracts information into a JSON list."},
        {"role": "user", "content": prompt_content}
    ]
    
    extracted_data = llm_call(messages)
    if extracted_data is None:
        return []
        
    for item in extracted_data:
        item['document'] = document['filename']
        
    return extracted_data


def reduce_and_rank_sections(all_sections, persona, task, input_documents_list):
    """REDUCE STEP: Creates the final, ranked output using a one-shot example."""
    print("Reducing and ranking all extracted sections...")

    prompt_content = f"""
    You are an expert editor. A junior researcher has provided a list of extracted sections. Your job is to analyze this list, then filter, merge, and rank the information to create a final report.

    **YOUR OUTPUT MUST STRICTLY FOLLOW THE FORMAT OF THIS EXAMPLE:**
    ---
    {EXAMPLE_OUTPUT}
    ---

    **User Persona:** {persona['role']}
    **User Task:** {task['task']}
    
    **Provided Sections to Analyze:**
    ---
    {json.dumps(all_sections, indent=2)}
    ---

    Now, generate the final JSON object for the provided sections.
    """

    messages = [
        {"role": "system", "content": "You are an expert editor that creates a final JSON report based on an example format."},
        {"role": "user", "content": prompt_content}
    ]

    final_json = llm_call(messages)
    if final_json and 'metadata' in final_json: # Check for metadata to help ensure it's the final object
         final_json['metadata'] = {
            "input_documents": input_documents_list,
            "persona": persona['role'],
            "job_to_be_done": task['task'],
            "processing_timestamp": datetime.datetime.now().isoformat()
        }
    return final_json


# --- Main Execution Logic ---
def main():
    """Main function to run the entire analysis pipeline."""
    print("--- Starting Challenge 1b (Final Version) ---")

    try:
        with open(INPUT_FILE, 'r') as f:
            input_data = json.load(f)
        persona = input_data["persona"]
        task = input_data["job_to_be_done"]
        documents = input_data["documents"]
        doc_filenames = [doc["filename"] for doc in documents]
        print("Successfully loaded input file.")
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    documents_content = extract_text_from_pdfs(doc_filenames)
    if not documents_content:
        print("No content extracted from PDFs. Exiting.")
        return

    all_extracted_sections = []
    for doc in documents_content:
        sections = map_document_to_sections(doc, persona, task)
        if sections and isinstance(sections, list): # Ensure we have a list
            all_extracted_sections.extend(sections)
    
    if not all_extracted_sections:
        print("--- No relevant sections found in the MAP step. ---")
        return

    final_output = reduce_and_rank_sections(all_extracted_sections, persona, task, doc_filenames)

    if final_output:
        try:
            with open(OUTPUT_FILE, 'w') as f:
                json.dump(final_output, f, indent=2)
            print(f"--- Success! Output saved to {OUTPUT_FILE} ---")
        except Exception as e:
            print(f"Error saving output file: {e}")
    else:
        print("--- Failed to generate final analysis in the REDUCE step. ---")

if __name__ == "__main__":
    main()