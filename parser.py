import json
from typing import Dict, List
from tokenizer import Tokenizer

class Parser:
    def __init__(self, tokenizer: Tokenizer):
        self.tokenizer = tokenizer

    def parse(self, file_path: str) -> Dict[str, Dict[str, List[str]]]:
        try:
            with open(file_path, "r") as file:
                data = json.load(file)

            parsed_data = {}
            
            # Iterate through categories
            for category in data.get("questions", []):
                category_name = category.get("category", "Unknown Category")
                parsed_data[category_name] = {"questions": [], "answers": []}

                # Tokenize each question and answer within the category
                for example in category.get("examples", []):
                    question = example.get("question", "")
                    answer = example.get("answer", "")
                    
                    question_tokens = self.tokenizer.tokenize(question)
                    answer_tokens = self.tokenizer.tokenize(answer)

                    parsed_data[category_name]["questions"].extend(question_tokens)
                    parsed_data[category_name]["answers"].extend(answer_tokens)

            return parsed_data

        except FileNotFoundError:
            print(f"File {file_path} not found.")
            return {}
        except json.JSONDecodeError:
            print(f"Invalid JSON format in {file_path}.")
            return {}
