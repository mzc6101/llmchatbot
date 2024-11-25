# llmchatbot
An On-Device LLM based Chatbot that answers user's queyries based on support and user-guide documentation scrapped using scrapy. Script creates FAQs based on chat history on the fly using chat history to create more relevant FAQs

Sonos Product Information Assistant

This project is a Flask-based web application designed to provide users with detailed information about Sonos products. Leveraging the Ollama API, the application processes user inquiries and delivers precise, context-aware responses.

Features

	•	Interactive Chat Interface: Users can engage in real-time conversations to obtain information about various Sonos products.
	•	Automated FAQ Generation: The system analyzes chat histories to generate and update a list of frequently asked questions, enhancing user experience.
	•	Product Data Integration: The application utilizes pre-scraped data from Sonos product pages to provide accurate and comprehensive responses.

Prerequisites

Before setting up the application, ensure the following are installed:
	•	Python 3.6 or higher
	•	Flask
	•	Requests library

Additionally, the Ollama API should be accessible and running locally.

Installation

	1.	Clone the Repository:

git clone https://github.com/yourusername/sonos-assistant.git
cd sonos-assistant


	2.	Set Up a Virtual Environment:

python3 -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate


	3.	Install Dependencies:

pip install -r requirements.txt


	4.	Configure the Application:
Ensure the Ollama API is running locally and accessible at http://127.0.0.1:11434/api. If it’s hosted elsewhere, update the OLLAMA_API_BASE variable in the script accordingly.
	5.	Prepare Sonos Product Data:
The application expects pre-scraped Sonos product data in JSON format, organized in the following directory structure:

sonos_scraper/
└── output/
    ├── arc/
    │   └── data.json
    ├── beam/
    │   └── data.json
    └── ... (other products)

Each data.json file should contain the product’s details, including paragraphs, headers, and lists.

Usage

	1.	Start the Application:

python app.py

By default, the application runs on http://0.0.0.0:5000.

	2.	Access the Chat Interface:
Navigate to http://localhost:5000 in your web browser to interact with the assistant.
	3.	Chat Endpoint:
	•	URL: /chat
	•	Method: POST
	•	Payload:

{
  "message": "Your question about a Sonos product"
}


	•	Response:

{
  "response": "Assistant's answer"
}


	4.	Generate Endpoint:
	•	URL: /generate
	•	Method: POST
	•	Payload:

{
  "message": "Your prompt for content generation"
}


	•	Response:

{
  "response": "Generated content"
}


	5.	FAQs Endpoint:
	•	URL: /faqs
	•	Method: GET
	•	Response:

{
  "faqs": "List of frequently asked questions and answers"
}



Logging

The application utilizes Python’s built-in logging module to record debug and error messages. Logs are displayed in the console and can be redirected to a file by configuring the logging settings in the script.

Thread Safety

To ensure thread-safe operations, especially when accessing or modifying shared resources like chat history and FAQs, the application employs threading locks.

Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your enhancements or bug fixes.

License

This project is licensed under the MIT License. See the LICENSE file for details.

Acknowledgments

Special thanks to the developers of Flask and the Ollama API for providing the tools that made this project possible.
