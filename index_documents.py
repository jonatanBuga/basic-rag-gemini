import fitz
import sys
import os
from docx import Document
from pathlib import Path
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from google import genai
import psycopg2
import psycopg2.extras
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..'))) # Add the parent directory to the path sicnce we work with notebooks

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

class pdf_To_Text:
    """
    A utility class to extract text from a PDF file.

    Attributes:
        file (str): The path to the PDF file.
        text_after_parsing (str): The extracted text from the PDF.
    """
    def __init__(self,path_to_pdf):
        """
        Initializes the pdf_To_Text instance and automatically extracts text from the given PDF.

        Args:
            pdf (str): The path to the PDF file.
        """
        self.file_path  = path_to_pdf
        self.text_after_parsing = ""
        self.extract_Text()
        

    def extract_Text(self):
        """
        Extracts text from all pages of the PDF file and stores it in the 'text_after_parsing' attribute.
        """
        try:
            with fitz.open(self.file_path) as pdf_file:
                for page in pdf_file:
                    self.text_after_parsing += page.get_text()
        except Exception as e:
            print(f"An error occurred while extracting text from the PDF: {e}")
            self.text_after_parsing = ""
        
         
    def get_text(self):
        """
        Returns the extracted text from the PDF.

        Returns:
            str: The text extracted from the PDF file.
        """
        return self.text_after_parsing
    

class docx_To_Text:
    """
    A utility class to extract text from a DOCX file.

    Attributes:
        file (str): The path to the DOCX file.
        text_after_parsing (str): The extracted text from the DOCX.
    """
    def __init__(self, path_to_docx):
        """
        Initializes the docx_To_Text instance and automatically extracts text from the given DOCX.

        Args:
            docx (str): The path to the DOCX file.
        """
        self.file_path = path_to_docx
        self.text_after_parsing = ""
        self.extract_Text()

    def extract_Text(self):
        """
        Extracts text from the DOCX file and stores it in the 'text_after_parsing' attribute.
        """
        try:
            doc = Document(self.file_path)
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            self.text_after_parsing = '\n'.join(full_text)
        except Exception as e:
            print(f"An error occurred while extracting text from the DOCX: {e}")
            self.text_after_parsing = ""
    def get_text(self):
        """
        Returns the extracted text from the DOCX.

        Returns:
            str: The text extracted from the DOCX file.
        """
        return self.text_after_parsing


class RAGPipeline:
    """
    A class to handle the RAG (Retrieval-Augmented Generation) pipeline.

    Attributes:
        text_splitter (RecursiveCharacterTextSplitter): The text splitter used to split the text into manageable chunks.
    """
    def __init__(self):
        """
        Initializes the RAGPipeline instance with a RecursiveCharacterTextSplitter.
        """
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.client = genai.Client(api_key=gemini_api_key)

    def split_text(self, text):
        """
        Splits the provided text into smaller chunks.

        Args:
            text (str): The text to be split.

        Returns:
            list: A list of text chunks.
        """
        return self.text_splitter.split_text(text)
    def embed_text(self, text_chunks):
        """
        Embeds the provided text chunks in batches of 100 using Gemini embedding model.

        Args:
            text_chunks (list): A list of text chunks to be embedded.

        Returns:
            list: A list of all embeddings.
        """
        all_embeddings = []
        batch_size = 100

        for i in range(0, len(text_chunks), batch_size):
            batch = text_chunks[i:i + batch_size]
            result = self.client.models.embed_content(
                model="gemini-embedding-001",
                contents=batch
            )
            all_embeddings.extend(result.embeddings)
        return all_embeddings
    def store_to_db(self, text_chunks, embeddings,filename):
        """
        Stores the text chunks and their corresponding embeddings in the PostgreSQL database.

        Args:
            text_chunks (list): A list of text chunks.
            embeddings (list): A list of embedding vectors corresponding to each text chunk.
            filename (str): The name of the source file for the chunks.
        """
        try:
            conn = psycopg2.connect(
                database="rag_pipeline",
                user='postgres',
                password='Lb318352978',
                host='localhost',
                port='5432'
            )
            cursor = conn.cursor()

            split_strategy = "Fixed-size with overlap"

            for chunk, embedding in zip(text_chunks, embeddings):
                cursor.execute("""
                    INSERT INTO document_chunks (chunk_text, embedding, source_name, split_strategy)
                    VALUES (%s, %s, %s, %s)
                """, (chunk, embedding, filename, split_strategy))

            conn.commit()
            print("✅ Data inserted successfully.")
        except Exception as e:
            print(f"❌ Error inserting data into DB: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

if __name__ == "__main__":
    # Example usage
    file_path = "simple_food_blog.pdf"
    pipeline = RAGPipeline()
    suffix = Path(file_path).suffix.lower()
    if suffix == ".pdf":
        pdf_extractor = pdf_To_Text(file_path)
        text_chunks = pipeline.split_text(pdf_extractor.get_text())
        emdedded_chunks = pipeline.embed_text(text_chunks)
        for i, (chunk, embedding) in enumerate(zip(text_chunks, emdedded_chunks)):
            print(f"Chunk {i+1}:")
            print("Text:", chunk)
            print("Embedding:", embedding)
            print("\n" + "="*50 + "\n")
    elif suffix == ".docx":
        docx_extractor = docx_To_Text(file_path)
        text_chunks = pipeline.split_text(docx_extractor.get_text())
        emdedded_chunks = pipeline.embed_text(text_chunks)
        for i, (chunk, embedding) in enumerate(zip(text_chunks, emdedded_chunks)):
            print(f"Chunk {i+1}:")
            print("Text:", chunk)
            print("Embedding:", embedding)
            print("\n" + "="*50 + "\n")
    else:
        print("Unsupported file format. Please provide a .pdf or .docx file.")
