from flask import Flask, render_template, request, jsonify
import os
import json
from datetime import datetime

# Flask app initialization
app = Flask(__name__)

# Paths for logs and database
current_directory = os.getcwd()
txt_file_path = os.path.join(current_directory, 'logs', 'logs.txt')
json_file_path = os.path.join(current_directory, 'logs', 'database.json')

# Ensure the logs and database exist
def ensure_files_exist():
    if not os.path.exists(os.path.join(current_directory, 'logs')):
        os.makedirs(os.path.join(current_directory, 'logs'))
    if not os.path.isfile(txt_file_path):
        with open(txt_file_path, 'w') as txt_file:
            txt_file.write("Conversation Logs:\n")
    if not os.path.isfile(json_file_path):
        with open(json_file_path, 'w') as json_file:
            json.dump([], json_file)

# Load database from JSON
def load_database():
    with open(json_file_path, 'r') as json_file:
        return json.load(json_file)

# Save database to JSON
def save_database(data):
    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

# Append to log file
def append_to_txt(question, answer):
    with open(txt_file_path, 'a') as txt_file:
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] Question: '{question}', Answer: '{answer}'\n"
        txt_file.write(log_entry)

# API endpoint for chatting
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    question = data['question']
    
    # Load the database
    database = load_database()

    # Check if the question exists in the database
    response = next((entry['answer'] for entry in database if entry['question'] == question), None)

    if not response:
        response = f"Sorry, I don't know the answer to '{question}'."
    
    # Log the chat in the .txt file
    append_to_txt(question, response)

    return jsonify({'answer': response})

# API endpoint for adding new data
@app.route('/add', methods=['POST'])
def add_to_database():
    data = request.json
    question = data['question']
    answer = data['answer']
    
    # Load the database
    database = load_database()

    # Add the new entry
    new_entry = {
        "question": question,
        "answer": answer,
        "timestamp": datetime.now().isoformat()
    }
    database.append(new_entry)
    
    # Save the updated database
    save_database(database)

    return jsonify({'message': 'Added successfully!'})

# Home route
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    ensure_files_exist()
    app.run(debug=True)
