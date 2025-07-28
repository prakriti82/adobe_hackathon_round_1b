

from sentence_transformers import SentenceTransformer, util


model = SentenceTransformer("all-MiniLM-L6-v2")

def rank_sections_by_similarity(sections, query):
    """
    Ranks a list of text sections against a query using semantic similarity.
    """
    if not sections:
        return []

    section_texts = [f"{s['title']}: {s['text'][:512]}" for s in sections]
    
    query_embedding = model.encode(query, convert_to_tensor=True)
    section_embeddings = model.encode(section_texts, convert_to_tensor=True)

    similarities = util.pytorch_cos_sim(query_embedding, section_embeddings)[0]
    
    ranked_results = sorted(zip(similarities, sections), key=lambda x: x[0], reverse=True)
    return [section for score, section in ranked_results]