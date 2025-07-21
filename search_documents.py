import sys
import os
from dotenv import load_dotenv
from google import genai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import psycopg2

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..'))) # Add the parent directory to the path sicnce we work with notebooks
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")


def fetch_embeddings_from_db():
    """
    Fetches all text chunks and their embeddings from the database.

    Returns:
        dict: {text_chunk: embedding_list}
    """
    conn = psycopg2.connect(
                database="rag_pipeline",
                user='postgres',
                password='Lb318352978',
                host='localhost',
                port='5432'
            )
    cursor = conn.cursor()
    cursor.execute('SELECT "chank_text", "Embedding" FROM document_chanks')
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    return {row[0]: row[1] for row in records}

def calculate_top5_similarities(embedding_query, embedding_dict):
    """
    Calculates the top 5 most similar embeddings to the query embedding.

    Args:
        embedding_query (list): Embedding vector of the user query.
        embedding_dict (dict): {text_chunk: embedding_list}

    Returns:
        list: List of tuples [(text, similarity_score), ...]
    """
    texts = list(embedding_dict.keys())
    vectors = list(embedding_dict.values())

    similarities = cosine_similarity([embedding_query], vectors)[0]
    top_indices = np.argsort(similarities)[-5:][::-1]

    return [(texts[i], float(similarities[i])) for i in top_indices]

def embed_text_single(text):
    client = genai.Client()
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )
    return response.embeddings[0].values
if __name__ == "__main__":
    user_input = input("Enter your query: ")
    embedding_query = embed_text_single(user_input)
    embedding_dict = fetch_embeddings_from_db()
    top5_similarities = calculate_top5_similarities(embedding_query, embedding_dict)
    print("\n Top 5 most similar text chunks:")
    for i, (text, score) in enumerate(top5_similarities, 1):
        print(f"{i}. Score: {score:.4f}")
        print(f"   Text: {text[:250]}...\n")


