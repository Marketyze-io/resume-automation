import logging
logging.basicConfig(level=logging.DEBUG)
#from pyresparser import ResumeParser
import requests
from flask import Flask, request, jsonify
import os
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials
import time
import openai
import httpx


# Ensure you have your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


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

    logging.debug("Listed files in folder!")
    return files

def download_file(file_id, file_name):
    request = drive_service.files().get_media(fileId=file_id)
    with open(file_name, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
    
    logging.debug("File is downloaded!")
    return file_name

import chardet
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']


def extract_info_from_resume(file_path):
    logging.debug("Loading resume...")

    # Detect file encoding
    encoding = detect_encoding(file_path)
    logging.debug(f"Detected encoding: {encoding}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            resume_content = f.read()
            print("UTF-8 Encoding used!")
    except UnicodeDecodeError:
        # If UTF-8 fails, try a different encoding
        try:
            with open(file_path, 'r', encoding='ISO-8859-1') as f:
                resume_content = f.read()
                logging.debug("ISO-8859-1 Encoding used!")
        except UnicodeDecodeError as e:
            logging.error(f"Error reading {file_path}: {e}")
            return {}
    
    # with open(file_path, 'rb') as f:
    #     resume_content = f.read()

    # Convert resume content to string if it's not already -- commented out as it is repetitive
    # if the file is opened successfully in either encoding, there's no need to check for bytes and decode it again
    # if isinstance(resume_content, bytes):
    #     resume_content = resume_content.decode('utf-8')

    # Construct the prompt
    prompt = f"Extract the following information from the resume:\n\n- Name\n- Email\n- University\n- Major\n\nResume:\n{resume_content}"

    logging.debug("Querying GPT now")

    retries=3
    delay=5

    for attempt in range(retries):
        try:
            # Make a call to the OpenAI API
            response = openai.completions.create(
                model="gpt-3.5-turbo-instruct",
                # model="text-davinci-003",
                prompt=prompt,
                max_tokens=200,
                temperature=0.5
            )

            # Extract the relevant information from the response
            gpt_output = response.choices[0].text.strip()

            # Parse the GPT output
            info = {}
            for line in gpt_output.split('\n'):
                if "Name:" in line:
                    info['name'] = line.split("Name:")[1].strip()
                elif "Email:" in line:
                    info['email'] = line.split("Email:")[1].strip()
                elif "University:" in line:
                    info['university'] = line.split("University:")[1].strip()
                elif "Major:" in line:
                    info['major'] = line.split("Major:")[1].strip()

            # Handle missing fields with default values
            info.setdefault('name', 'Unknown Name')
            info.setdefault('email', 'unknown@unknown.com')
            info.setdefault('university', 'Unknown University')
            info.setdefault('major', 'Unknown Major')

            logging.debug("Resume loaded.")
            return info

        

        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error occurred: {e} - Status Code: {e.response.status_code}")
            if e.response.status_code == 429:  # Too Many Requests
                logging.warning(f"Rate limit exceeded. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logging.error(f"HTTP Error: {e}")
                break  # Stop retrying on other HTTP errors
        except httpx.RequestError as e:
            logging.error(f"Request error occurred: {e}")
            break  # Stop retrying on request errors
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            logging.error(f"{e.response.status_code}")
            if e.response.status_code == 429:  # Too Many Requests
                logging.warning(f"Rate limit exceeded. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logging.error(f"Other Error: {e}")
                break

    return {}


def add_to_notion(info):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    # Replace 'university_name' with the name parsed from the resume
    university_name = info.get('university', 'Unknown University')

    # Find the corresponding university in the dropdown options
    university_options = {
        "Chulalongkorn University": "e4620776-71b2-40ef-b6e4-ee9587f96964",
        "Thammasat University": "a7deee28-61ac-4cc0-a6c4-5eee9d54a624",
        "Kasetsart University": "6316161c-a8ae-4728-8947-8f890fe70fdb",
        "Mahidol University": "7a6b4b91-2073-4011-a2a9-ec4598839d4f",
        "Mahidol University International College": "0e0ef175-c024-40cc-8b5c-38cf5cc2f658",
        "Srinakharinwirot University": "cbc2f335-2254-4fe1-a00f-d5b4a28dec05",
        "University of British Columbia": "94a16bd9-46b3-4c62-8eaf-5834b62c6578",
        "Tokyo International University": "16614773-dd1f-400c-b5e1-4c047b940764",
        "Naresuan University International College": "224be10c-3ffb-448d-acef-9d01aa6f64c9",
        "National University Singapore": "e66780d2-c7df-45aa-9156-8c827e18cf0d",
        "University of Dundee": "e09764a5-0be2-4345-8803-8fb061485e84",
        "New York University": "fcaa6621-7ee7-4902-856d-d1892039665d"
    }

    university_id = university_options.get(university_name, "Other University")
    
    logging.debug("Start processing data to be sent to Notion!")

    data = {
        "parent": { "database_id": database_id },
        "properties": {

            # "Name": {
            #     "id": "title",
            #     #"name": "Name",
            #     # "type": "title",
            #     # "title": {info.get('name', 'Unknown Name') }
            #     # "title": [{
            #     #     "text": { 
            #     #         # "content": f"{info.get('first_name', 'Unknown First Name')} {info.get('last_name', 'Unknown Last Name')}" 
            #     #         "content": f"{info.get('name', 'Unknown Name')}" 
            #     #     }
            #     # }]
            #     "title": [{ 
            #         "text": { 
            #             # "content": f"{info.get('first_name', 'Unknown First Name')} {info.get('last_name', 'Unknown Last Name')}" 
            #             "content": f"{info.get('name', 'Unknown Name')}" 
            #         }
            #     }]
            # },

            "Name": { 
                "title": [{ 
                    "text": {  
                        "content": f"{info.get('name', 'Unknown Name')}" 
                    }
                }]
            },

            "Email": {
                # "id": "n%3AN.",
                # "name": "Email",
                # "type": "email",
                #"email": {info.get('email', 'unknown@unknown.com')}
                "email": [{ 
                    "text": {  
                        "content": f"{info.get('name', 'Unknown Name')}" 
                    }
                }]
            },

            # "University": {
            #     "id": "%7Ccl%3D",
            #     "name": "University",
            #     "type": "select",
            #     "select": {
            #         "name": university_name
            #     }
            # } if university_id else {},  # Only include this if the university matches

            # "Major": {
            #     "id": "3.%3BY",
            #     "name": "Major",
            #     "type": "rich_text",
            #     "rich_text": {info.get('major', 'Unknown Major')}
            # },
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
    
    logging.debug("Data sent to Notion!")
    return response.json()


@app.route('/process_drive_folder', methods=['POST'])
def process_drive_folder():
    files = list_files_in_folder(google_drive_folder_id)
    responses = []
    for file in files:
        try:
            file_path = download_file(file['id'], file['name'])
            logging.debug("FILE DOWNLOADED")
            info = extract_info_from_resume(file_path)
            logging.debug("INFO EXTRACTED FROM RESUME")
            response = add_to_notion(info)
            responses.append(response)
        except Exception as e:
            responses.append({"error": str(e)})
    return jsonify(responses)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    if os.name == "nt":  # Check if the OS is Windows (nt)
        from waitress import serve
        serve(app, host='0.0.0.0', port=port)
    else:
        app.run(debug=True, host='0.0.0.0', port=port)