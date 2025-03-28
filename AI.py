import os
import json
import requests
from tkinter import Tk, Entry, Button, Text, Menu, Frame, Scrollbar, VERTICAL, RIGHT, Y, BOTH, END
from tokenizer import Tokenizer
from parser import Parser
from datetime import datetime

# File names
json_file = os.path.join(os.getcwd(), "data.json")
log_directory = "chat_logs"

# API details (replace with your actual keys)
GOOGLE_API_KEY = "AIzaSyAOWpfGiWw4P0syufQFjqS3Mu0qqku_76g"  # Replace with your Google Custom Search API Key
SEARCH_ENGINE_ID = "b089ae631e86a4503"  # Replace with your Search Engine ID
WEATHERSTACK_API_KEY = "38c8546006f2fe33452b70b05f8895d9S"  # Replace with your Weatherstack API Key

# Ensure the chat_logs directory exists
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Load data from the JSON file
def load_data():
    try:
        if not os.path.exists(json_file):  # Create file if it doesn't exist
            with open(json_file, "w") as file:
                json.dump({"questions": []}, file)
        with open(json_file, "r") as file:
            content = file.read().strip()
            return json.loads(content) if content else {"questions": []}
    except json.JSONDecodeError:
        return {"questions": []}

# Function to query Google Custom Search API
def search_google(query):
    url = f"https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": query,
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json()
        extracted_data = []
        for item in results.get("items", []):
            summary = item.get("snippet", "No description available")
            extracted_data.append(f"{item.get('title', 'No title')}: {summary}")
        return extracted_data
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []

# Function to query Weatherstack API
def get_weather(location):
    url = f"http://api.weatherstack.com/current"
    params = {
        "access_key": WEATHERSTACK_API_KEY,
        "query": location,
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if "current" in data:
            weather = {
                "location": data["location"]["name"],
                "temperature": data["current"]["temperature"],
                "description": data["current"]["weather_descriptions"][0],
                "humidity": data["current"]["humidity"]
            }
            return weather
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# Function to detect the type of query
def detect_query_type(user_message):
    user_message = user_message.lower()
    if "weather" in user_message and "in" in user_message:
        return "weather"
    elif "search" in user_message:
        return "search"
    else:
        return "general"

# Save updated data back to the JSON file
def save_data(data):
    with open(json_file, "w") as file:
        json.dump(data, file, indent=4)

# Function to log the conversation to a file
def log_chat(chat_name, username, conversation):
    log_file = os.path.join(log_directory, f"{chat_name}.txt")
    with open(log_file, "a") as log:
        log.write(f"Chat with {username} on {datetime.now()}\n")
        log.write("\n".join(conversation) + "\n\n")

# Function to find an answer in the dataset
def find_answer(question, data, parser):
    question = question.lower().strip()
    for category in data.get("questions", []):
        for example in category.get("examples", []):
            if example.get("question", "").lower() == question:
                return example.get("answer")
    return None

# GUI application class
class ChatGPTLikeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ChatGPT-like Bot")
        self.data = load_data()
        self.tokenizer = Tokenizer(lowercase=True, remove_punctuation=True)
        self.parser = Parser(tokenizer=self.tokenizer)
        self.username = os.getlogin()
        self.conversation = []
        self.current_chat = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create main widgets
        self.main_frame = Frame(root)
        self.main_frame.pack(fill=BOTH, expand=True)

        self.chat_display = Text(self.main_frame, height=20, width=80, wrap="word", state="disabled")
        self.chat_display.pack(side="left", fill=BOTH, expand=True)

        self.scrollbar = Scrollbar(self.main_frame, orient=VERTICAL, command=self.chat_display.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.chat_display.config(yscrollcommand=self.scrollbar.set)

        self.entry_frame = Frame(root)
        self.entry_frame.pack(fill=BOTH)

        self.entry_box = Entry(self.entry_frame, width=60)
        self.entry_box.pack(side="left", padx=5, pady=5)
        self.entry_box.bind("<Return>", self.on_enter_key)  # Link Enter key to send_message

        self.send_button = Button(self.entry_frame, text="Send", command=self.send_message)
        self.send_button.pack(side="left", padx=5, pady=5)

    def on_enter_key(self, event):
        """Handles the 'Enter' key press."""
        self.send_message()

    def send_message(self):
        user_message = self.entry_box.get().strip()
        if user_message:
            self.display_message(f"You: {user_message}")
            self.conversation.append(f"You: {user_message}")

            query_type = detect_query_type(user_message)
            if query_type == "weather":
                # Extract location from the query
                location = user_message.split("in")[-1].strip()
                weather = get_weather(location)
                if weather:
                    self.display_message(f"Weather in {weather['location']}:\nTemperature: {weather['temperature']}°F\nDescription: {weather['description']}\nHumidity: {weather['humidity']}%")
                else:
                    self.display_message("Sorry, I couldn't retrieve the weather information.")
            elif query_type == "search":
                search_query = user_message.replace("search", "").strip()
                search_results = search_google(search_query)
                if search_results:
                    for result in search_results[:3]:  # Display top 3 summarized results
                        self.display_message(result)
                else:
                    self.display_message("No search results found.")
            else:
                bot_response = find_answer(user_message, self.data, self.parser) or "Sorry, I don't know the answer."
                self.display_message(f"Bot: {bot_response}")
                self.conversation.append(f"Bot: {bot_response}")

            self.entry_box.delete(0, END)

    def display_message(self, message):
        self.chat_display.config(state="normal")
        self.chat_display.insert(END, f"{message}\n")
        self.chat_display.config(state="disabled")
        self.chat_display.see(END)

# Start the Tkinter application
if __name__ == "__main__":
    root = Tk()
    app = ChatGPTLikeApp(root)
    root.mainloop()
