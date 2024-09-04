from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials
#from pyresparser import ResumeParser
import httpx
import logging
logging.basicConfig(level=logging.DEBUG)
import os
import PyPDF2
import requests
import tiktoken
import time
import openai


# Ensure you have your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load Google credentials from environment variable
google_creds_json = os.getenv('GOOGLE_CREDS_JSON')
google_creds_json = {"type":"service_account","project_id":"automations-415608","private_key_id":"3874762116474ab5c6929a410191911fcc6426cb","private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCxvjfWhgwJJuPl\nvq8+W303YPz4VEglvdlhUmRiyOurUT28TG7BLqj0PiHWoFNVKUWNug7cArA2DhDD\nVeVq1NdM+SaT6PblqR064pagnuPh+ZrriRnrq9SR1v9TzdtLvFjhep77BkdyVfPQ\n07e8gyAwqCmreDBBIuVzbXiNolchKnTQpmHc2SeIbXKw2aqW+fdDrW4sFKxffQnf\nC0CwN97xPgj8yT5uUID7kKlfPKA+sGcvKeVHeSnkfDzjWszIG5O83xUZXihOHen+\nJdxSIun/klo4UeiaAu9b81Iajo/8IUpWEDsDlT34ChKf2h2VPXeOZb0MgW6tZYCw\nIV6kHh7hAgMBAAECggEABaQNqdpcdqxkKmoGLf6Rj2C9uoRTO1ZmeBUZMDzj5M6Z\n3NhYofsg+8pegM0bA+6AwXYUi2Uu8jI5VDetRZoOYKgeEi7gKgr3TWN8SAnu3cCy\nCtRRrSXpg7zc4swbT/Cg6fv+IGWTPiTN7XRQphQLwRuPIfzZHDIXMdX5L9aFeR0O\nBbY+Xx/9wxj5RLStPIq635ez6qMMv8Swdrb4x2jdto3bLDBxSymUpYqK47VhT3Yd\nORn8M2dfXGaKssAXe9C8mCHlrN7fLYp/Yl0K5rDD9gHIW4HBG9uAFxDC8EcUYpHm\nIafdSoEisxPo+QeJQSE0fGSPEZCCB1xPISVZbIh94QKBgQD10kwkK5TUmPhkBsiU\nJHrQ1fCfjKzkVypmOsHm9ry2U3wb5Zc4rVp1WPapNhMaDwwL2k3zU/qAl1zan64g\nCQffmp3BJj6SCIFOQdqpVn19VTHC7eSEUorfhel9kzOvsQ1+A9Wcgka8zNwkDjQg\nhraZ6C9xs8UrYGAYYDH8h181MQKBgQC5GkpqFJzhs8dLSsKVFuki2axQDNjNXOea\nrwyIP+bvRM4hNhNMtt5IbH+D6DO48naIA+vFOUJZI8c6WVz6yxTSkS+csLqfAZn4\nopfwwBVpnc7gNpzD0zPRbJqrTlls3jCPR7C9kbtoub5lWk41t3cM9pC0WmcrXJx6\ntBj6JrnYsQKBgFWK5wA3QkVxLg7w5V/YCf0eVevPsmKLiq+khtFuz2DLUIcMsEEC\n4lWvrbZYoPESh2iggTvJ34RcJ+3UX226dsjzLy6FtoRu/UBUXllLRcQVn4lr63e4\nmacLHKOcVAIxpLZTc0RReXg9+eV6I92lw2lviQMSQezETuxsnTh5i0IhAoGAQhUd\nvfNv8rABFWMyRpGwV63Ic6eyetaRJMsbuUS/CGrTAE5S449hmg+KEqiCVqPRJ0vn\nDzka88HvLWib5jk8TNRiYBlD9uJWesppXhzlSBh7s9Yrb0nmdPzF1ySYjmJgibZ5\nZaQyePfe/kYYJ9tA2FLqZEjmDjf48WF8jUnoDXECgYEA2kJDpgEP/Ae75oYwzYW0\n8pI81XviPfXGcRdgFYXh3NQibHAuuARi0LQZENqZ44AY3yuRDBrcIu/ou8U0jpUm\nR8WZI1ykMJlRr33G2BIp1Vi6HigTbDdifU+uE+YMpEvx6MJOFLjttPAEDjegD7km\nEAJEcgO7nnkhdeevPpaEY1A=\n-----END PRIVATE KEY-----\n","client_email":"resume-automation@automations-415608.iam.gserviceaccount.com","client_id":"101858961367440296504","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/resume-automation%40automations-415608.iam.gserviceaccount.com","universe_domain":"googleapis.com"}

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

notion_api_key = os.getenv("NOTION_API_KEY")
database_id = os.getenv("NOTION_DATABASE_ID")
google_drive_folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

# Initialize an empty list to store file names in the order they are added
file_order_list = []
new_file_added = 0

def list_files_in_folder(folder_id):
    global file_order_list
    global new_file_added
    new_file_added = 0  # Reset the counter each time the function is called

    query = f"'{folder_id}' in parents"
    # results = drive_service.files().list(q=query).execute()
    results = drive_service.files().list(q=query, orderBy="modifiedTime").execute()
    files = results.get('files', [])

    if not files:
        logging.info(f"No files found in Google Drive folder {folder_id}.")
        return None

    # Print the retrieved files to the logs
    logging.info(f"Files retrieved from Google Drive folder {folder_id}:")

    # Identify new files and update the list
    for file in files:
        # Display file name
        logging.info(f"File ID: {file['id']}, Name: {file['name']}")
        # Add file to file order list if not done so
        if file['name'] not in file_order_list:
            file_order_list.append(file['name'])
            logging.info(f"New file added to file order list: {file['name']}")
            new_file_added += 1
        else:
            logging.info(f"No new file added to file order list")

    logging.debug("Listed files in folder!")
    logging.debug("Updated file order list:")
    logging.debug(file_order_list)
    return files

def get_latest_file():
    global file_order_list
    global new_file_added
    
    if file_order_list and (new_file_added > 0):
        latest_file_name = file_order_list[-1] #Get the last file in the list
        logging.info(f"Latest file to process: {latest_file_name}")
        return latest_file_name
    else:
        logging.info("No files to process.")
        return None

def download_file(file_id, file_name):
    request = drive_service.files().get_media(fileId=file_id)
    with open(file_name, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
    
    logging.debug("File is downloaded!")
    return file_name

def download_file_by_name(file_name):
    query = f"name = '{file_name}' and '{google_drive_folder_id}' in parents"
    results = drive_service.files().list(q=query).execute()
    files = results.get('files', [])

    if files:
        file_id = files[0]['id']
        return download_file(file_id, file_name)
    else:
        logging.error(f"File {file_name} not found in Google Drive folder.")
        return None

import chardet
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

def print_tokens(text):
    tokenizer = tiktoken.get_encoding("cl100k_base")
    # tokenizer = tiktoken.encoding_for_model("gpt-4")
    tokens = tokenizer.encode(text)
    
    print(f"Total tokens: {len(tokens)}")
    print("Tokens:")
    for token in tokens:
        print(f"{token}: {tokenizer.decode([token])}")

def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_info_from_resume(file_path):
    logging.debug("Loading resume...")

    # Detect file encoding -- ONLY FOR TEXT FILES
    # encoding = detect_encoding(file_path)
    # logging.debug(f"Detected encoding: {encoding}")

    try:
        # Extract text from PDF
        resume_content = extract_text_from_pdf(file_path)
        logging.debug("Text extracted from PDF.")
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        return {}

# The following code block only works for text files instead of PDF
    # try:
    #     with open(file_path, 'r', encoding='utf-8') as f:
    #         resume_content = f.read()
    #         print("UTF-8 Encoding used!")
    # except UnicodeDecodeError:
    #     # If UTF-8 fails, try a different encoding
    #     try:
    #         with open(file_path, 'r', encoding='ISO-8859-1') as f:
    #             resume_content = f.read()
    #             logging.debug("ISO-8859-1 Encoding used!")
    #     except UnicodeDecodeError as e:
    #         logging.error(f"Error reading {file_path}: {e}")
    #         return {}
    
    # with open(file_path, 'rb') as f:
    #     resume_content = f.read()

    # Convert resume content to string if it's not already -- commented out as it is repetitive
    # if the file is opened successfully in either encoding, there's no need to check for bytes and decode it again
    # if isinstance(resume_content, bytes):
    #     resume_content = resume_content.decode('utf-8')

    # Construct the prompt
    # prompt = f"Extract the following information from the resume:\n\n- Name\n- Email\n- University\n- Major\n\nResume:\n{resume_content}"

    # Print the tokens to debug the tokenization process
    print_tokens(resume_content)

    # Construct the prompt for input text
    prompt = f"Extract the following information from the resume:\n\n- Name\n- Email\n- University\n- Major\n\nResume:\n{resume_content[:2000]}"
    # Truncate resume_content to a smaller length (e.g., 2000 characters) to stay within the token limit.

    logging.debug("Querying GPT now")

    retries=3
    delay=5

    for attempt in range(retries):
        try:
            # Make a call to the OpenAI API
            # response = openai.completions.create(     This line is legacy, only works for gpt-3.5-turbo-instruct, babbage-002, davinci-002
            response = openai.chat.completions.create(
                # model="gpt-3.5-turbo",
                # model="gpt-3.5-turbo-instruct",
                model="gpt-4-turbo",
                # model="text-davinci-003",
                messages = [{"role": "system", "content": prompt}],
                # prompt=prompt,
                max_tokens=200,
                temperature=0.5
            )

            # Log the entire response for debugging
            logging.debug(f"Full GPT Response: {response}")

            # Extract the relevant information from the response
            #gpt_output = response.choices[0].text.strip()
            gpt_output = response.choices[0].message.content.strip()

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

            "Name": { 
                "title": [{ 
                    "text": {  
                        "content": f"{info.get('name', 'Unknown Name')}" 
                    }
                }]
            },

            "Email": {
                "email": f"{info.get('email', 'unknown@unknown.com')}"                 
            },

            "University": {
                "select": {
                    "name": university_name if university_id else "Unknown University"
                }
            },

            "Major": {
                "rich_text": [{
                    "text": {
                        "content": f"{info.get('major', 'Unknown Major')}"
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
    
    logging.debug("Data sent to Notion!")
    return response.json()


@app.route('/process_drive_folder', methods=['POST'])
def process_drive_folder():
    # files = list_files_in_folder(google_drive_folder_id)
    # responses = []
    # for file in files:
    #     try:
    #         file_path = download_file(file['id'], file['name'])
    #         logging.debug("FILE DOWNLOADED")
    #         info = extract_info_from_resume(file_path)
    #         logging.debug("INFO EXTRACTED FROM RESUME")
    #         response = add_to_notion(info)
    #         logging.debug("ADDED TO NOTION")
    #         responses.append(response)
    #     except Exception as e:
    #         responses.append({"error": str(e)})
    # return jsonify(responses)

    list_files_in_folder(google_drive_folder_id)
    latest_file_name = get_latest_file()

    if latest_file_name:
        file_path = download_file_by_name(latest_file_name)
        logging.debug("FILE DOWNLOADED")
        info = extract_info_from_resume(file_path)
        logging.debug("INFO EXTRACTED FROM RESUME")
        response = add_to_notion(info)
        logging.debug("ADDED TO NOTION")
        return jsonify(response)
    else:
        return jsonify({"error": "No new files to process"})


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    if os.name == "nt":  # Check if the OS is Windows (nt)
        from waitress import serve
        serve(app, host='0.0.0.0', port=port)
    else:
        app.run(debug=True, host='0.0.0.0', port=port)