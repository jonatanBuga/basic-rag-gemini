import fitz
import sys
import os
from docx import Document
from pathlib import Path
import re
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..'))) # Add the parent directory to the path sicnce we work with notebooks

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

if __name__ == "__main__":
    # Example usage
    file_path = "simple_food_blog.pdf"
    suffix = Path(file_path).suffix.lower()
    if suffix == ".pdf":
        pdf_extractor = pdf_To_Text(file_path)
        print(pdf_extractor.get_text())
    elif suffix == ".docx":
        docx_extractor = docx_To_Text(file_path)
        print(docx_extractor.get_text())
    else:
        print("Unsupported file format. Please provide a .pdf or .docx file.")