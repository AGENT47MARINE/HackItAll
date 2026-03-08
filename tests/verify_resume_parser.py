import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from services.nlp.resume_parser_service import ResumeParserService
from services.nlp.extractors import LocalLLMExtractor

def test_pdf_extraction():
    # Since we can't easily create a real PDF, we'll mock the extraction
    # or use a very simple one if available.
    # For now, let's just test the parse_resume logic with raw text.
    parser = ResumeParserService()
    
    sample_text = """
    John Doe
    Email: john@example.com
    Experience: 
    - Full Stack Developer at Tech Corp. Used React, Node.js, and PostgreSQL.
    - Intern at AI Soft. Worked on Python and TensorFlow.
    Education:
    - B.Tech in Computer Science from XYZ University.
    Interests:
    - Artificial Intelligence, Open Source, and Cryptography.
    """
    
    print("Testing parse_resume with sample text...")
    result = parser.parse_resume(sample_text)
    print("Extracted Profile Data:")
    print(result)
    
    # Assertions (basic)
    assert "skills" in result
    assert "interests" in result
    assert "education_level" in result
    print("Test Passed!")

if __name__ == "__main__":
    test_pdf_extraction()
