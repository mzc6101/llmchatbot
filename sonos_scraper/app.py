import requests
from flask import Flask, request, jsonify, render_template
import os
import logging
import json
import re
import threading

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)

# Lock for thread-safe operations
lock = threading.Lock()

# Paths for storing chat history and FAQs
CHAT_HISTORY_FILE = 'chat_history.json'
FAQ_FILE = 'faqs.json'

# Function to load Sonos data from JSON files
def load_sonos_data(output_dir='./sonos_scraper/output/'):
    sonos_data = {}
    if not os.path.exists(output_dir):
        logging.error(f"Output directory not found at {output_dir}")
        return sonos_data

    for product_folder in os.listdir(output_dir):
        product_path = os.path.join(output_dir, product_folder)
        data_file = os.path.join(product_path, 'data.json')
        if os.path.isfile(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    sonos_data[product_folder.lower()] = data
                    logging.debug(f"Loaded data for product: {product_folder.lower()}")
                except json.JSONDecodeError as e:
                    logging.error(f"Error decoding JSON for product {product_folder.lower()}: {e}")
        else:
            logging.warning(f"No data.json found for product: {product_folder.lower()}")
    return sonos_data

sonos_data = load_sonos_data()

# Define Ollama API endpoints
OLLAMA_API_BASE = "http://127.0.0.1:11434/api"
CHAT_ENDPOINT = f"{OLLAMA_API_BASE}/chat"
GENERATE_ENDPOINT = f"{OLLAMA_API_BASE}/generate"

# Define synonyms for product names
product_synonyms = {
    'arc': ['arc', 'sonos arc'],
    'beam': ['beam', 'sonos beam'],
    'ray': ['ray', 'sonos ray'],
    'sub': ['sub', 'sonos sub'],
    'roam': ['roam', 'sonos roam'],
    'move': ['move', 'sonos move'],
    'five': ['five', 'sonos five'],
    'one': ['one', 'sonos one'],
    'amp': ['amp', 'sonos amp'],
    'boost': ['boost', 'sonos boost'],
    'port': ['port', 'sonos port'],
    's1': ['s1', 'sonos s1'],
    # Add more products and their synonyms as needed
}

def extract_product_name(user_input, product_synonyms):
    """
    Extracts the product name from the user input using synonyms.
    Returns the canonical product name if found, else None.
    """
    for canonical_name, synonyms in product_synonyms.items():
        for synonym in synonyms:
            pattern = r'\b' + re.escape(synonym.lower()) + r'\b'
            if re.search(pattern, user_input.lower()):
                return canonical_name
    return None

def save_chat_history(user_input, assistant_response):
    """Saves the conversation to the chat history file."""
    with lock:
        if os.path.exists(CHAT_HISTORY_FILE):
            with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
                chat_history = json.load(f)
        else:
            chat_history = []

        chat_history.append({
            'user': user_input,
            'assistant': assistant_response
        })

        with open(CHAT_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(chat_history, f, ensure_ascii=False, indent=4)

def generate_faqs():
    """Generates FAQs using Ollama based on the chat history."""
    with lock:
        with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
            chat_history = json.load(f)

    # Prepare the prompt for FAQ generation
    conversation_text = ''
    for convo in chat_history:
        conversation_text += f"User: {convo['user']}\nAssistant: {convo['assistant']}\n\n"

    prompt = (
        "Based on the following conversations about Sonos products, generate a list of FAQs with concise answers.\n\n"
        f"{conversation_text}\n"
        "FAQs:\n"
    )

    payload = {
        "model": "llama3.2",
        "prompt": prompt,
        "max_tokens": 500,
        "temperature": 0.5,
        "stream": False
    }

    headers_req = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(GENERATE_ENDPOINT, json=payload, headers=headers_req, timeout=60)
        response.raise_for_status()
        ollama_response = response.json()
        faqs = ollama_response.get('response', '').strip()

        with lock:
            with open(FAQ_FILE, 'w', encoding='utf-8') as f:
                f.write(faqs)

    except requests.exceptions.RequestException as e:
        logging.error(f"Error generating FAQs with Ollama: {e}")
    except (KeyError, TypeError) as e:
        logging.error(f"Error processing Ollama response: {e}")

def check_and_update_faqs():
    """Checks if FAQs need to be generated or updated."""
    with lock:
        if os.path.exists(CHAT_HISTORY_FILE):
            with open(CHAT_HISTORY_FILE, 'r', encoding='utf-8') as f:
                chat_history = json.load(f)
        else:
            chat_history = []

    if len(chat_history) >= 10:
        generate_faqs()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_input = data.get("message", "").strip()
    except:
        user_input = ""

    if not user_input:
        assistant_response = "Please enter a valid question."
        save_chat_history(user_input, assistant_response)
        return jsonify({"response": assistant_response})

    # Extract product name from user input
    product_name = extract_product_name(user_input, product_synonyms)

    if not product_name:
        assistant_response = "I'm sorry, I can only assist with questions related to Sonos products. Please specify a Sonos product."
        save_chat_history(user_input, assistant_response)
        return jsonify({"response": assistant_response})

    # Retrieve relevant data for the product
    product_info = sonos_data.get(product_name.lower(), {})
    paragraphs = product_info.get('paragraphs', [])
    headers = product_info.get('headers', [])
    lists = product_info.get('lists', [])

    if not (paragraphs or headers or lists):
        assistant_response = f"Sorry, I couldn't find information about the Sonos {product_name.title()}."
        save_chat_history(user_input, assistant_response)
        return jsonify({"response": assistant_response})

    # Combine the data into a well-structured format using HTML ordered list
    relevant_data = ""
    for header, paragraph, lst in zip(headers, paragraphs, lists):
        relevant_data += f"<h3>{header}</h3>\n<p>{paragraph}</p>\n<ol>"
        for item in lst:
            relevant_data += f"<li>{item}</li>\n"
        relevant_data += "</ol>\n"

    # Combine Sonos data with user input to create the prompt
    prompt = (
        f"You are an expert on Sonos products. Only answer questions related to Sonos. "
        f"Use only the information provided below to answer the user's question.\n\n"
        f"{relevant_data}\n\n"
        f"User: {user_input}\n"
        f"Assistant:"
    )

    logging.debug(f"Generated Prompt: {prompt}")

    # Prepare the payload for the /api/chat endpoint
    payload = {
        "model": "llama3.2",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False 
    }

    headers_req = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(CHAT_ENDPOINT, json=payload, headers=headers_req, timeout=60)
        response.raise_for_status()
        ollama_response = response.json()
        logging.debug(f"Ollama Response: {ollama_response}")

        # Extract the assistant's response
        assistant_message = ollama_response.get('message', {})
        assistant_response = assistant_message.get('content', '').strip()

    except requests.exceptions.RequestException as e:
        logging.error(f"Error communicating with Ollama API: {e}")
        assistant_response = f"Error generating response: {e}"
    except (KeyError, TypeError) as e:
        logging.error(f"Unexpected response structure: {e}")
        assistant_response = "Received an unexpected response from the model."

    if not assistant_response:
        assistant_response = "The model could not generate a response. Please try again."

    # Save the conversation to chat history
    save_chat_history(user_input, assistant_response)

    # Check and update FAQs if necessary
    check_and_update_faqs()

    return jsonify({"response": assistant_response})

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json()
        user_input = data.get("message", "").strip()
    except:
        user_input = ""

    if not user_input:
        assistant_response = "Please enter a valid prompt."
        save_chat_history(user_input, assistant_response)
        return jsonify({"response": assistant_response})

    # Extract product name from user input
    product_name = extract_product_name(user_input, product_synonyms)

    if not product_name:
        assistant_response = "I'm sorry, I can only assist with questions related to Sonos products. Please specify a Sonos product."
        save_chat_history(user_input, assistant_response)
        return jsonify({"response": assistant_response})

    # Retrieve relevant data for the product
    product_info = sonos_data.get(product_name.lower(), {})
    paragraphs = product_info.get('paragraphs', [])
    headers = product_info.get('headers', [])
    lists = product_info.get('lists', [])

    if not (paragraphs or headers or lists):
        assistant_response = f"Sorry, I couldn't find information about the Sonos {product_name.title()}."
        save_chat_history(user_input, assistant_response)
        return jsonify({"response": assistant_response})

    # Combine the data into a well-structured format
    relevant_data = ""
    for header, paragraph, lst in zip(headers, paragraphs, lists):
        relevant_data += f"{header}\n{paragraph}\n"
        for item in lst:
            relevant_data += f"- {item}\n"
        relevant_data += "\n"

    # Prepare the prompt with updated instructions
    prompt = (
        f"You are an expert on Sonos products. Only answer questions related to Sonos. "
        f"Use only the information provided below to answer the user's question.\n\n"
        f"{relevant_data}\n\n"
        f"User: {user_input}\n"
        f"Assistant:\n"
        f"Please provide a neatly formatted response without any asterisks or unnecessary quotation marks. "
        f"Use plain text, and list each step or bullet point on a new line."
    )

    logging.debug(f"Generated Prompt for Completion: {prompt}")

    # Prepare the payload for the /api/generate endpoint
    payload = {
        "model": "llama3.2",
        "prompt": prompt,
        "max_tokens": 200,
        "temperature": 0.7,
        "stream": False
    }

    headers_req = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(GENERATE_ENDPOINT, json=payload, headers=headers_req, timeout=60)
        response.raise_for_status()
        ollama_response = response.json()
        logging.debug(f"Ollama Generate Response: {ollama_response}")

        # Extract the assistant's response
        assistant_response = ollama_response.get('response', '').strip()

        # Post-process the response
        assistant_response = assistant_response.replace('*', '').replace('"', '')
        assistant_response = re.sub(r'(\d+\.\s*)', r'\n\1', assistant_response)
        assistant_response = re.sub(r'(-\s*)', r'\n\1', assistant_response)
        assistant_response = assistant_response.strip()

    except requests.exceptions.RequestException as e:
        logging.error(f"Error communicating with Ollama API: {e}")
        assistant_response = f"Error generating completion: {e}"
    except (KeyError, TypeError) as e:
        logging.error(f"Unexpected response structure: {e}")
        assistant_response = "Received an unexpected response from the model."

    if not assistant_response:
        assistant_response = "The model could not generate a completion. Please try again."

    # Save the conversation to chat history
    save_chat_history(user_input, assistant_response)

    # Check and update FAQs if necessary
    check_and_update_faqs()

    return jsonify({"response": assistant_response})

@app.route("/faqs", methods=["GET"])
def get_faqs():
    """Returns the generated FAQs."""
    with lock:
        if os.path.exists(FAQ_FILE):
            with open(FAQ_FILE, 'r', encoding='utf-8') as f:
                faqs = f.read()
        else:
            faqs = "FAQs are not available yet. Please check back later."

    return jsonify({"faqs": faqs})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)