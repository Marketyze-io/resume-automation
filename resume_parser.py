from pyresparser import ResumeParser
import requests
from flask import Flask, request, jsonify
import os
import nltk

# Download required NLTK data files
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

app = Flask(__name__)

notion_api_key = os.getenv("NOTION_API_KEY", "your_notion_api_key")
database_id = os.getenv("NOTION_DATABASE_ID", "your_database_id")

def extract_info_from_resume(file_path):
    data = ResumeParser(file_path).get_extracted_data()
    if data:
        return {
            "first_name": data.get("name", "").split()[0],
            "last_name": data.get("name", "").split()[-1],
            "mobile_no": data.get("mobile_number", ""),
            "university": data.get("college_name", ""),
            "linkedin_profile": data.get("linkedin", ""),
            "cv": file_path
        }
    return {}

def add_to_notion(info):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    data = {
        "parent": { "database_id": database_id },
        "properties": {
            "First Name": { "title": [{ "text": { "content": info.get("first_name", "") }}]},
            "Last Name": { "rich_text": [{ "text": { "content": info.get("last_name", "") }}]},
            "Mobile No": { "phone_number": info.get("mobile_no", "") },
            "University": { "rich_text": [{ "text": { "content": info.get("university", "") }}]},
            "LinkedIn Profile": { "url": info.get("linkedin_profile", "") },
            "CV": { "files": [{ "name": "CV", "external": { "url": info.get("cv", "") }}]}
        }
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()  # This will raise an HTTPError for bad responses
    return response.json()

@app.route('/process_resume', methods=['POST'])
def process_resume():
    resume_files = request.json.get('resume_files', [])
    responses = []
    for resume in resume_files:
        try:
            info = extract_info_from_resume(resume)
            response = add_to_notion(info)
            responses.append(response)
        except Exception as e:
            responses.append({"error": str(e)})
    return jsonify(responses)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    if os.getenv("FLASK_ENV") == "development":
        app.run(debug=True, host='0.0.0.0', port=port)
    else:
        from waitress import serve
        serve(app, host='0.0.0.0', port=port)
