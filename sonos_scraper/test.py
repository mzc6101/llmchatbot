import ollama

def test_ollama():
    prompt = "Tell me about Sonos products."
    try:
        response = ollama.chat(model='llama2:7b', messages=[{'role': 'user', 'content': prompt}])
        print("Assistant Response:", response.get('message', {}).get('content', 'No content'))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_ollama()