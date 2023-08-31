from flask import Flask, render_template, request, jsonify
import openai
import json
import requests
import os
from bs4 import BeautifulSoup

# Configure OpenAI API key
openai_api_key = os.getenv('OPENAI_API_KEY')
extractor_api = os.getenv('EXTRACTOR_API')
openai.api_key = openai_api_key

app = Flask(__name__)

# Define the chat function as provided
def chat(system, user_assistant):
    system_msg = [{"role": "system", "content": system}]
    user_assistant_msgs = [{"role": "user", "content": user_assistant}]
    msgs = system_msg + user_assistant_msgs
    response = openai.ChatCompletion.create(model="gpt-4", messages=msgs)
    return response["choices"][0]["message"]["content"]

def get_webpage_content(url):
    
    extractor_api_url = f"https://extractorapi.com/api/v1/extractor/?apikey={extractor_api}&url={url}"
    response = requests.get(extractor_api_url)
    if response.status_code == 200:
        data = json.loads(response.text)
        return data["text"]
    else:
        return None

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        links = request.form.getlist('link')
        data = []
        for link in links:
            content = get_webpage_content(link)
            if content:
                print(content)
                words = content.split()
                if len(words) > 5000:
                    content = ' '.join(words[:5000])
                prompt = (
        "You are the data protection and data privacy expert. Given the content of product / service related page, "
        "you will analyse and determine what are the relevant consent requirements. Your response will only be in the json format based on the example given below. Remember that this is just an example and your content will appropriately change based on the content of the page and the company.:\n"
        "{\n"
        "  \"consentRequirements\": [\n"
        "    {\n"
        "      \"purpose\": \"Personal Loan Application\",\n"
        "      \"collectionMethods\": [\n"
        "        \"online form\",\n"
        "        \"document submission\"\n"
        "      ],\n"
        "      \"lawfulBasis\": \"performance of a contract\",\n"
        "      \"personalDataTypes\": [\n"
        "        \"personal identification information\",\n"
        "        \"financial information\",\n"
        "        \"contact information\",\n"
        "        \"employment information\",\n"
        "        \"credit history\"\n"
        "      ],\n"
        "      \"thirdParties\": [\n"
        "        \"credit bureaus\"\n"
        "      ],\n"
        "      \"expiry\": \"2 years\"\n"
        "    },\n"
        "    {\n"
        "      \"purpose\": \"Marketing offers\",\n"
        "      \"collectionMethods\": [\n"
        "        \"online form\"\n"
        "      ],\n"
        "      \"lawfulBasis\": \"consent\",\n"
        "      \"personalDataTypes\": [\n"
        "        \"personal identification information\",\n"
        "        \"contact information\",\n"
        "        \"financial information\"\n"
        "      ],\n"
        "      \"thirdParties\": [\n"
        "        \"Affiliates and Partners\"\n"
        "      ],\n"
        "      \"expiry\": \"1 year\"\n"
        "    }\n"
        "  ]\n"
        "}"
    )
                analysis = chat(prompt, content)
                data.append(json.loads(analysis))
            else:
                print(f"Failed to fetch content for {link}")
        return render_template('table.html', data=data)
    return render_template('index.html')

@app.route('/api/analyze', methods=['GET'])
def analyze_api():
    link = request.args.get('link')
    if link is None:
        return jsonify({"error": "Link parameter is required"}), 400

    content = get_webpage_content(link)
    if content:
        print(content)
        words = content.split()
        if len(words) > 5000:
            content = ' '.join(words[:5000])
        prompt = (
        "You are the data protection and data privacy expert. Given the content of product / service related page, "
        "you will analyse and determine what are the relevant consent requirements. Your response will only be in the json format based on the example given below. Remember that this is just an example and your content will appropriately change based on the content of the page and the company.:\n"
        "{\n"
        "  \"consentRequirements\": [\n"
        "    {\n"
        "      \"purpose\": \"Personal Loan Application\",\n"
        "      \"collectionMethods\": [\n"
        "        \"online form\",\n"
        "        \"document submission\"\n"
        "      ],\n"
        "      \"lawfulBasis\": \"performance of a contract\",\n"
        "      \"personalDataTypes\": [\n"
        "        \"personal identification information\",\n"
        "        \"financial information\",\n"
        "        \"contact information\",\n"
        "        \"employment information\",\n"
        "        \"credit history\"\n"
        "      ],\n"
        "      \"thirdParties\": [\n"
        "        \"credit bureaus\"\n"
        "      ],\n"
        "      \"expiry\": \"2 years\"\n"
        "    },\n"
        "    {\n"
        "      \"purpose\": \"Marketing offers\",\n"
        "      \"collectionMethods\": [\n"
        "        \"online form\"\n"
        "      ],\n"
        "      \"lawfulBasis\": \"consent\",\n"
        "      \"personalDataTypes\": [\n"
        "        \"personal identification information\",\n"
        "        \"contact information\",\n"
        "        \"financial information\"\n"
        "      ],\n"
        "      \"thirdParties\": [\n"
        "        \"Affiliates and Partners\"\n"
        "      ],\n"
        "      \"expiry\": \"1 year\"\n"
        "    }\n"
        "  ]\n"
        "}"
    )
        analysis = chat(prompt, content)
        return analysis
    else:
        return jsonify({"error": f"Failed to fetch content for {link}"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
