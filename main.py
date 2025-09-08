# import os
# import uuid
# from fastapi import FastAPI, File, UploadFile

# app = FastAPI()

# # Store resumes temporarily in current working directory
# UPLOAD_DIR = os.path.dirname(__file__)  
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# @app.post("/upload-resume")
# async def upload_resume(file: UploadFile = File(...)):
#     file_id = str(uuid.uuid4())
#     temp_filename = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

#     with open(temp_filename, "wb") as f:
#         f.write(await file.read())

#     # ✅ Call your pipeline here instead of dummy return
#     parsed_data = {"message": f"Temp file saved at {temp_filename}"}

#     # Optionally delete file after parsing:
#     # os.remove(temp_filename)

#     return parsed_data

import os
from dotenv import load_dotenv
load_dotenv()
import uuid
import json
from fastapi import FastAPI, File, UploadFile, HTTPException
from parsers.pipeline import parse_resume
from parsers.extractor import extract_text_from_pdf, extract_text_from_docx

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

    # ✅ Extract text based on file type
    if extension == "pdf":
        resume_text = extract_text_from_pdf(temp_filename)
    elif extension == "docx":
        resume_text = extract_text_from_docx(temp_filename)

    # ✅ Pass extracted text to parser
    parsed_data = parse_resume(resume_text)

    # ✅ Save parsed JSON
    json_filename = os.path.join(UPLOAD_DIR, f"{file_id}.json")
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(parsed_data.dict(), f, ensure_ascii=False, indent=4)

    # Optionally delete the uploaded file
    os.remove(temp_filename)

    return {"message": f"Parsed data saved as {json_filename}", "parsed_data": parsed_data}
