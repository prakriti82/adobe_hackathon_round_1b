# heading_utils.py

import fitz  # PyMuPDF
import statistics

def get_most_common_font_size(page):
    """Helper function to find the most common font size for body text."""
    font_sizes = [span['size'] for block in page.get_text("dict")['blocks'] for line in block['lines'] for span in line['spans']]
    if not font_sizes:
        return 10  # Default size
    return statistics.mode(font_sizes)

def extract_headings_and_text(doc_path, filename):
    """
    Extracts sections from a PDF by identifying headings based on font size
    and then capturing the text that follows each heading.
    """
    try:
        doc = fitz.open(doc_path)
    except Exception as e:
        print(f"Error opening {filename}: {e}")
        return []

    sections = []
    
    for page_num, page in enumerate(doc, start=1):
        # Determine a threshold for what constitutes a "heading"
        base_font_size = get_most_common_font_size(page)
        heading_threshold = base_font_size * 1.15  # e.g., anything 15% larger is a heading

        blocks = page.get_text("dict")["blocks"]
        current_heading = None
        current_text = ""

        for i, block in enumerate(blocks):
            if 'lines' in block:
                # Check the first line of the block for heading potential
                first_line_spans = block['lines'][0]['spans']
                if not first_line_spans:
                    continue
                
                span_size = first_line_spans[0]['size']
                span_text = " ".join([s['text'] for s in first_line_spans]).strip()

                # If we find a new heading
                if span_size >= heading_threshold and len(span_text.split()) < 15:
                    # Save the previously collected section
                    if current_heading:
                        sections.append({
                            "title": current_heading,
                            "text": current_text.strip(),
                            "page": page_num,
                            "document": filename
                        })
                    
                    # Start a new section
                    current_heading = span_text
                    current_text = ""
                else:
                    # Otherwise, append the block's text to the current section
                    block_text = " ".join([line['spans'][0]['text'] for line in block['lines'] if line['spans']])
                    current_text += block_text + "\n"

        # Add the last section found on the page
        if current_heading:
            sections.append({
                "title": current_heading,
                "text": current_text.strip(),
                "page": page_num,
                "document": filename
            })
            
    return sections