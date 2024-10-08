from pyresparser import ResumeParser
import requests
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

notion_api_key = os.getenv("NOTION_API_KEY")
database_id = os.getenv("NOTION_DATABASE_ID")

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

# The error ModuleNotFoundError: No module named 'fcntl' occurs because the fcntl module 
# is specific to Unix-like operating systems (such as Linux and macOS) and is not available on Windows.

# How to Resolve the Issue
# Since you're working on a Windows environment, you'll need to 
# avoid using any functionality that relies on fcntl when running your application locally on Windows. 

# if __name__ == "__main__":
#     port = int(os.environ.get('PORT', 5000))
#     if os.getenv("FLASK_ENV") == "development":
#         app.run(debug=True, host='0.0.0.0', port=port) # If Linux or Mac
#     else:
#         from waitress import serve
#         serve(app, host='0.0.0.0', port=port) # If windows

# Explanation:
# os.name: The check os.name == "nt" is the correct way to determine if the script is running on a Windows system. 
# nt refers to Windows NT, and this is a reliable way to identify the Windows environment.

# FLASK_ENV: Using FLASK_ENV to distinguish between development and production environments is common, 
# but in this case, since the problem is platform-specific, checking the operating system is a better approach.

# Summary:
# Windows: Uses waitress for serving the application.
# Linux/Mac: Uses the default Flask server (or you can add the option to run gunicorn).

# Operating System Check: I've replaced the FLASK_ENV check with os.name == "nt", 
# which directly checks if the environment is Windows. 
# This ensures that waitress is only used when the application is running on Windows.

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    if os.name == "nt":  # Check if the OS is Windows (nt)
        from waitress import serve
        serve(app, host='0.0.0.0', port=port)
    else:
        app.run(debug=True, host='0.0.0.0', port=port)