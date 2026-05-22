import os
from google import genai

# Manual .env read
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('GEMINI_API_KEY='):
                os.environ['GEMINI_API_KEY'] = line.split('=')[1].strip()

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("No GEMINI_API_KEY found")
else:
    client = genai.Client(api_key=api_key)
    try:
        models = client.models.list()
        for m in models:
            print(m.name)
    except Exception as e:
        print(f"Error listing models: {e}")
