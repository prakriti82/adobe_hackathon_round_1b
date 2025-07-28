
import fitz  
import statistics

def get_most_common_font_size(page):
    """Helper function to find the most common font size for body text."""
    font_sizes = [span['size'] for block in page.get_text("dict")['blocks'] for line in block['lines'] for span in line['spans']]
    if not font_sizes:
        return 10  
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
        base_font_size = get_most_common_font_size(page)
        heading_threshold = base_font_size * 1.15  

        blocks = page.get_text("dict")["blocks"]
        current_heading = None
        current_text = ""

        for i, block in enumerate(blocks):
            if 'lines' in block:
                first_line_spans = block['lines'][0]['spans']
                if not first_line_spans:
                    continue
                
                span_size = first_line_spans[0]['size']
                span_text = " ".join([s['text'] for s in first_line_spans]).strip()

                if span_size >= heading_threshold and len(span_text.split()) < 15:
                    if current_heading:
                        sections.append({
                            "title": current_heading,
                            "text": current_text.strip(),
                            "page": page_num,
                            "document": filename
                        })
                    
                    current_heading = span_text
                    current_text = ""
                else:
                    block_text = " ".join([line['spans'][0]['text'] for line in block['lines'] if line['spans']])
                    current_text += block_text + "\n"

        if current_heading:
            sections.append({
                "title": current_heading,
                "text": current_text.strip(),
                "page": page_num,
                "document": filename
            })
            
    return sections