import re
from typing import List

class Tokenizer:
    def __init__(self, lowercase: bool = True, remove_punctuation: bool = True):
        self.lowercase = lowercase
        self.remove_punctuation = remove_punctuation

    def tokenize(self, text: str) -> List[str]:
        # Convert text to lowercase if specified
        if self.lowercase:
            text = text.lower()

        # Remove punctuation if specified
        if self.remove_punctuation:
            text = re.sub(r'[^\w\s]', '', text)

        # Split text into tokens (words)
        tokens = text.split()
        return tokens
