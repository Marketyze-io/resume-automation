import logging
logging.basicConfig(level=logging.INFO)
from pyresparser import ResumeParser
import requests
from flask import Flask, request, jsonify
import os
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials


# Load Google credentials from environment variable
# google_creds_json = os.getenv('GOOGLE_CREDS_JSON')

google_creds_json = {
  "type": "service_account",
  "project_id": "automations-415608",
  "private_key_id": "3874762116474ab5c6929a410191911fcc6426cb",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCxvjfWhgwJJuPl\nvq8+W303YPz4VEglvdlhUmRiyOurUT28TG7BLqj0PiHWoFNVKUWNug7cArA2DhDD\nVeVq1NdM+SaT6PblqR064pagnuPh+ZrriRnrq9SR1v9TzdtLvFjhep77BkdyVfPQ\n07e8gyAwqCmreDBBIuVzbXiNolchKnTQpmHc2SeIbXKw2aqW+fdDrW4sFKxffQnf\nC0CwN97xPgj8yT5uUID7kKlfPKA+sGcvKeVHeSnkfDzjWszIG5O83xUZXihOHen+\nJdxSIun/klo4UeiaAu9b81Iajo/8IUpWEDsDlT34ChKf2h2VPXeOZb0MgW6tZYCw\nIV6kHh7hAgMBAAECggEABaQNqdpcdqxkKmoGLf6Rj2C9uoRTO1ZmeBUZMDzj5M6Z\n3NhYofsg+8pegM0bA+6AwXYUi2Uu8jI5VDetRZoOYKgeEi7gKgr3TWN8SAnu3cCy\nCtRRrSXpg7zc4swbT/Cg6fv+IGWTPiTN7XRQphQLwRuPIfzZHDIXMdX5L9aFeR0O\nBbY+Xx/9wxj5RLStPIq635ez6qMMv8Swdrb4x2jdto3bLDBxSymUpYqK47VhT3Yd\nORn8M2dfXGaKssAXe9C8mCHlrN7fLYp/Yl0K5rDD9gHIW4HBG9uAFxDC8EcUYpHm\nIafdSoEisxPo+QeJQSE0fGSPEZCCB1xPISVZbIh94QKBgQD10kwkK5TUmPhkBsiU\nJHrQ1fCfjKzkVypmOsHm9ry2U3wb5Zc4rVp1WPapNhMaDwwL2k3zU/qAl1zan64g\nCQffmp3BJj6SCIFOQdqpVn19VTHC7eSEUorfhel9kzOvsQ1+A9Wcgka8zNwkDjQg\nhraZ6C9xs8UrYGAYYDH8h181MQKBgQC5GkpqFJzhs8dLSsKVFuki2axQDNjNXOea\nrwyIP+bvRM4hNhNMtt5IbH+D6DO48naIA+vFOUJZI8c6WVz6yxTSkS+csLqfAZn4\nopfwwBVpnc7gNpzD0zPRbJqrTlls3jCPR7C9kbtoub5lWk41t3cM9pC0WmcrXJx6\ntBj6JrnYsQKBgFWK5wA3QkVxLg7w5V/YCf0eVevPsmKLiq+khtFuz2DLUIcMsEEC\n4lWvrbZYoPESh2iggTvJ34RcJ+3UX226dsjzLy6FtoRu/UBUXllLRcQVn4lr63e4\nmacLHKOcVAIxpLZTc0RReXg9+eV6I92lw2lviQMSQezETuxsnTh5i0IhAoGAQhUd\nvfNv8rABFWMyRpGwV63Ic6eyetaRJMsbuUS/CGrTAE5S449hmg+KEqiCVqPRJ0vn\nDzka88HvLWib5jk8TNRiYBlD9uJWesppXhzlSBh7s9Yrb0nmdPzF1ySYjmJgibZ5\nZaQyePfe/kYYJ9tA2FLqZEjmDjf48WF8jUnoDXECgYEA2kJDpgEP/Ae75oYwzYW0\n8pI81XviPfXGcRdgFYXh3NQibHAuuARi0LQZENqZ44AY3yuRDBrcIu/ou8U0jpUm\nR8WZI1ykMJlRr33G2BIp1Vi6HigTbDdifU+uE+YMpEvx6MJOFLjttPAEDjegD7km\nEAJEcgO7nnkhdeevPpaEY1A=\n-----END PRIVATE KEY-----\n",
  "client_email": "resume-automation@automations-415608.iam.gserviceaccount.com",
  "client_id": "101858961367440296504",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/resume-automation%40automations-415608.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}


# google_creds_json = {
#     "web":{
#     "client_id":"434069935105-ofp9sru97mf5vh650mc37l2n16ve9kme.apps.googleusercontent.com",
#     "project_id":"automations-415608",
#     "auth_uri":"https://accounts.google.com/o/oauth2/auth",
#     "token_uri":"https://oauth2.googleapis.com/token",
#     "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
#     "client_secret":"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",???????
#     "redirect_uris":["https://resume-automation.onrender.com/oauth2callback"],????
#     "javascript_origins":["https://resume-automation.onrender.com"]?????
#     }
# }

# google_creds_json = {
#     "type": "service_account",?????
#     "project_id":"automations-415608",
#     "private_key_id": "your-private-key-id",?????????????????
#     "private_key": "your-private-key",?????????????????
#     "client_email": "your-client-email@your-project-id.iam.gserviceaccount.com",?????????????
#     "client_id":"434069935105-ofp9sru97mf5vh650mc37l2n16ve9kme.apps.googleusercontent.com",
#     "auth_uri":"https://accounts.google.com/o/oauth2/auth",
#     "token_uri":"https://oauth2.googleapis.com/token",
#     "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
#     "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-client-email%40your-project-id.iam.gserviceaccount.com"?????
# }


# The error you're encountering is because you're trying to load a dictionary (google_creds_json) 
# using json.loads(), which expects a JSON string, not a dictionary. 
# Since you already have the JSON content as a dictionary, # you don't need to use json.loads(). 
# You can pass the dictionary directly to Credentials.from_service_account_info().

app = Flask(__name__)

if google_creds_json:
    creds = Credentials.from_service_account_info(google_creds_json)
else:
    raise ValueError("Google credentials not found in environment variables")

drive_service = build('drive', 'v3', credentials=creds)

notion_api_key = os.getenv("NOTION_API_KEY", "secret_5gwBVqjZDAC99Okj3HbrwIbSKwxOJYkpl1QE40mQDXW")
database_id = os.getenv("NOTION_DATABASE_ID", "a4ab10ca7b27411ebcb3664b04c1d399")
google_drive_folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "10P2DQDZZKIGKId8WcLSxMloSpTaeMjB3")

def list_files_in_folder(folder_id):
    query = f"'{folder_id}' in parents"
    results = drive_service.files().list(q=query).execute()
    files = results.get('files', [])

    # Print the retrieved files to the logs
    logging.info(f"Files retrieved from Google Drive folder {folder_id}:")
    for file in files:
        logging.info(f"File ID: {file['id']}, Name: {file['name']}")

    return files

# def download_file(file_id, file_name):
#     request = drive_service.files().get_media(fileId=file_id)
#     fh = open(file_name, 'wb')
#     downloader = MediaIoBaseDownload(fh, request)
#     done = False
#     while done is False:
#         status, done = downloader.next_chunk()
#     return file_name

def download_file(file_id, file_name):
    request = drive_service.files().get_media(fileId=file_id)
    with open(file_name, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
    return file_name


def extract_info_from_resume(file_path):
    logging.debug("Loading resume...")
    data = ResumeParser(file_path).get_extracted_data()
    print(data) # See how the data looks like after parsing by ResumeParser
    logging.debug("Resume loaded.")

    if data:
        name = data.get("name")
        # Handle name splitting safely
        if name:
            name_parts = name.split()
            first_name = name_parts[0] if len(name_parts) > 0 else "Unknown"
            last_name = name_parts[-1] if len(name_parts) > 1 else "Unknown"
        else:
            name = "Unknown"
            first_name = "Unknown"
            last_name = "Unknown"

        return {
            "first_name": first_name,
            "last_name": last_name,
            "name": name,
            "email": data.get("email", "unknown@unknown.com"),
            "mobile_no": data.get("mobile_number", "No Number Provided"),
            "university": data.get("college_name", "No University Provided"),
            "linkedin_profile": data.get("linkedin", "No LinkedIn"),
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
    # data = {
    #     "parent": { "database_id": database_id },
    #     "properties": {
    #         "First NameF": { "title": [{ "text": { "content": info.get("first_name", "") }}]},
    #         "Last Name": { "rich_text": [{ "text": { "content": info.get("last_name", "") }}]},
    #         "Mobile No": { "phone_number": info.get("mobile_no", "") },
    #         "University": { "rich_text": [{ "text": { "content": info.get("university", "") }}]},
    #         "LinkedIn Profile": { "url": info.get("linkedin_profile", "") },
    #         "CV": { "files": [{ "name": "CV", "external": { "url": info.get("cv", "") }}]}
    #     }
    # }

    data = {
        "parent": { "database_id": database_id },
        "properties": {
            "Name": { 
                "title": [{ 
                    "text": { 
                        # "content": f"{info.get('first_name', 'Unknown First Name')} {info.get('last_name', 'Unknown Last Name')}" 
                        "content": f"{info.get('name', 'Unknown Name')}" 
                    }
                }]
            },
            "Email": { 
                "email": info.get('email', 'unknown@unknown.com')
            },
            "University": { 
                "rich_text": [{ 
                    "text": { 
                        "content": info.get("university", "No University Provided") 
                    }
                }]
            },
        }
    }

    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # This will raise an HTTPError for bad responses
        print(response.json())
    except requests.exceptions.HTTPError as e:
        # Check if the error is due to email validation
        if "validation_error" in str(response.content) and "Email is expected to be email." in str(response.content):
            print("Error: The email field is not properly formatted.")
        else:
            print(f"HTTP Error: {e}")
        print(f"Response Content: {response.content}")
        return {"error": f"Failed to add page to Notion: {e}"}
    except Exception as e:
        # Handle other possible errors
        print(f"An unexpected error occurred: {e}")
        return {"error": f"An unexpected error occurred: {e}"}
    
    return response.json()


@app.route('/process_drive_folder', methods=['POST'])
def process_drive_folder():
    files = list_files_in_folder(google_drive_folder_id)
    responses = []
    for file in files:
        try:
            file_path = download_file(file['id'], file['name'])
            info = extract_info_from_resume(file_path)
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
    port = int(os.environ.get('PORT', 10000))
    if os.name == "nt":  # Check if the OS is Windows (nt)
        from waitress import serve
        serve(app, host='0.0.0.0', port=port)
    else:
        app.run(debug=True, host='0.0.0.0', port=port)