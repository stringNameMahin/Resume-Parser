import os
from google.cloud import secretmanager
import uuid
import json
from fastapi import FastAPI, File, UploadFile, HTTPException
from parsers.pipeline import parse_resume
from parsers.extractor import extract_text_from_pdf, extract_text_from_docx

def get_api_key_from_secret(secret_name: str, project_id: str) -> str:
    """
    Fetch the secret value from Google Secret Manager
    """
    client = secretmanager.SecretManagerServiceClient()
    secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(name=secret_path)
    return response.payload.data.decode("UTF-8")

PROJECT_ID = "abstract-stream-471415-r8"
SECRET_NAME = "resume-parser-env"
API_KEY = get_api_key_from_secret(SECRET_NAME, PROJECT_ID)

app = FastAPI()

UPLOAD_DIR = os.path.dirname(__file__)
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    extension = file.filename.split(".")[-1].lower()

    if extension not in ["pdf", "docx"]:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")

    temp_filename = os.path.join(UPLOAD_DIR, f"{file_id}.{extension}")
    with open(temp_filename, "wb") as f:
        f.write(await file.read())

    if extension == "pdf":
        resume_text = extract_text_from_pdf(temp_filename)
    elif extension == "docx":
        resume_text = extract_text_from_docx(temp_filename)

    parsed_data = parse_resume(resume_text, api_key=API_KEY)

    json_filename = os.path.join(UPLOAD_DIR, f"{file_id}.json")
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(parsed_data.dict(), f, ensure_ascii=False, indent=4)

    os.remove(temp_filename)

    return {"message": f"Parsed data saved as {json_filename}", "parsed_data": parsed_data}
