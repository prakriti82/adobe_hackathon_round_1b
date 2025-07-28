# semantic_utils.py

from sentence_transformers import SentenceTransformer, util

# This model will be downloaded automatically by the library the first time.
# It's a small but powerful model, perfect for this task.
model = SentenceTransformer("all-MiniLM-L6-v2")

def rank_sections_by_similarity(sections, query):
    """
    Ranks a list of text sections against a query using semantic similarity.
    """
    if not sections:
        return []

    # The model works better if we combine the title and a snippet of text
    section_texts = [f"{s['title']}: {s['text'][:512]}" for s in sections]
    
    # Encode the query and all section texts
    query_embedding = model.encode(query, convert_to_tensor=True)
    section_embeddings = model.encode(section_texts, convert_to_tensor=True)

    # Calculate cosine similarities
    similarities = util.pytorch_cos_sim(query_embedding, section_embeddings)[0]
    
    # Pair similarities with their original sections and sort
    ranked_results = sorted(zip(similarities, sections), key=lambda x: x[0], reverse=True)
    
    # Return just the sorted sections
    return [section for score, section in ranked_results]