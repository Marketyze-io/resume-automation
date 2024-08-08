from pyresparser import ResumeParser
import requests
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

notion_api_key = "your_notion_api_key"
database_id = "your_database_id"

def extract_info_from_resume(file_path):
    data = ResumeParser(file_path).get_extracted_data()
    return {
        "first_name": data.get("name").split()[0],
        "last_name": data.get("name").split()[-1],
        "mobile_no": data.get("mobile_number"),
        "university": data.get("college_name"),
        "linkedin_profile": data.get("linkedin"),
        "cv": file_path
    }

def add_to_notion(info):
    url = f"https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    data = {
        "parent": { "database_id": database_id },
        "properties": {
            "First Name": { "title": [{ "text": { "content": info["first_name"] }}]},
            "Last Name": { "rich_text": [{ "text": { "content": info["last_name"] }}]},
            "Mobile No": { "phone_number": info["mobile_no"] },
            "University": { "rich_text": [{ "text": { "content": info["university"] }}]},
            "LinkedIn Profile": { "url": info["linkedin_profile"] },
            "CV": { "files": [{ "name": "CV", "external": { "url": info["cv"] }}]}
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

@app.route('/process_resume', methods=['POST'])
def process_resume():
    resume_files = request.json.get('resume_files', [])
    responses = []
    for resume in resume_files:
        info = extract_info_from_resume(resume)
        response = add_to_notion(info)
        responses.append(response)
    return jsonify(responses)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
