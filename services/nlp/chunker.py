import re

class SemanticHTMLChunker:
    """Chunks cleaned HTML text into manageable sizes for LLM context windows."""
    
    def __init__(self, chunk_size: int = 12000, overlap: int = 1000):
        self.chunk_size = chunk_size
        self.overlap = overlap
        
    def chunk(self, text: str) -> list:
        """Splits text into chunks, trying to break at semantic boundaries (newlines)."""
        if len(text) <= self.chunk_size:
            return [text]
            
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            if end >= len(text):
                chunks.append(text[start:])
                break
                
            # Search for a good breaking point (double newline or single newline)
            break_point = text.rfind('\n\n', start, end)
            if break_point == -1 or break_point < start + (self.chunk_size // 2):
                break_point = text.rfind('\n', start, end)
                
            if break_point == -1 or break_point < start + (self.chunk_size // 2):
                # Fallback to last space
                break_point = text.rfind(' ', start, end)
                
            if break_point == -1:
                # Absolute fallback: just cut
                break_point = end
                
            chunks.append(text[start:break_point].strip())
            start = break_point - self.overlap if break_point > self.overlap else break_point
            
        return chunks
