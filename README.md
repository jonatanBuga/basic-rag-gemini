# RAG Pipeline: Indexing and Searching Documents with Embeddings

This project demonstrates a complete RAG (Retrieval-Augmented Generation) pipeline using a local PostgreSQL database, Gemini embeddings, and document chunking.

---

## 📦 Part 1 – Indexing Documents

### 🧱 Setup Instructions
1. **Clone the project & navigate to directory:**
   ```bash
   git clone https://github.com/jonatanBuga/basic-rag-gemini.git
   cd basic-rag-gemini 
   ׳׳׳ 
2. Install dependencies:  
    pip install -r requirements.txt 
3. Add your Gemini API key in .env : 
    GEMINI_API_KEY=your_key_here 
4. Setup PostgreSQL using Docker : 
    Make sure Docker is installed, then run - 
        ```bash
        docker-compose up --build
        ׳׳׳ 
    This spins up a PostgreSQL server with a database named rag_pipeline
5. Run the RAG indexing pipeline : 
    python3 index_documents.py 
    **No arguments are required. The script processes a sample PDF already included in the repository** (simple_food_blog.pdf)
6. Once completed successfully, the text chunks and their embeddings are inserted into the PostgreSQL table document_chanks


## Part 2 – Searching Top 5 Similar Chunks
### This part retrieves the top 5 text chunks most similar to a user's query using cosine similarity. 

### 💡 How to use
1. run this command - python3 search_documents.py

You will be prompted to enter a query,The script will return the 5 most relevant text chunks from the database, along with their similarity score 

2. ✨ Example queries to try: 
    * How do I make orange syrup for a cake with orange blossom water?
    * Should I pour the syrup before or after serving the cake?
    * What is the purpose of using polenta in a cake recipe?
    * Can I store the cake in the fridge after baking it?

## ✅ Notes
* All embeddings are stored as FLOAT8[] arrays in PostgreSQL
* Chunks are split using the "Fixed-size with overlap" strategy
* The index_documents.py file handles chunking, embedding, and storing
* The search_documents.py file handles querying and similarity comparison





