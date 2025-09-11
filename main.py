import os
from google.cloud import secretmanager
from fastapi import FastAPI, File, UploadFile, HTTPException
from parsers.pipeline import parse_resume
from parsers.extractor import extract_text_from_pdf, extract_text_from_docx
from langchain_google_genai import ChatGoogleGenerativeAI

app = FastAPI()
UPLOAD_DIR = os.path.dirname(__file__)
os.makedirs(UPLOAD_DIR, exist_ok=True)

PROJECT_ID = "abstract-stream-471415-r8"
SECRET_NAME = "resume-parser-env"

def get_api_key_from_secret(secret_name: str, project_id: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(name=secret_path)
    return response.payload.data.decode("UTF-8")

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    extension = file.filename.split(".")[-1].lower()

    if extension not in ["pdf", "docx"]:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")

    file_content = await file.read()

    if extension == "pdf":
        resume_text = extract_text_from_pdf(file_content)
    elif extension == "docx":
        resume_text = extract_text_from_docx(file_content)

    # Fetch secret and create LLM instance here
    api_key = get_api_key_from_secret(SECRET_NAME, PROJECT_ID)
    llm_instance = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0, google_api_key=api_key)

    parsed_data = parse_resume(resume_text, llm=llm_instance)

    return {"parsed_data": parsed_data}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
