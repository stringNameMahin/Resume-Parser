# parsers/pipeline.py
import os
import datetime
from typing import Tuple

from google.cloud import secretmanager
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from parsers.schema import parser, prompt


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

def _get_default_llm():
    return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0, google_api_key=API_KEY)

def parse_resume(resume_text: str, links: list = None, llm=None):
    """Run LLM chain to parse resume into structured object."""
    if llm is None:
        llm = _get_default_llm()

    chain = LLMChain(llm=llm, prompt=prompt)
    llm_output: str = chain.run(resume_text=resume_text)

    parsed = parser.parse(llm_output)

    if links:
        existing_socials = set(parsed.socials or [])
        extracted_links = set(link["uri"] for link in links)
        merged_socials = list(existing_socials.union(extracted_links))
        parsed.socials = merged_socials

    return parsed


def map_to_firestore_schema(parsed, file_url: str) -> Tuple[dict, dict, dict]:
    """Map parsed object into Firestore-like schema."""
    now = datetime.datetime.utcnow()

    name = getattr(parsed, "name", "") or ""
    education_list = getattr(parsed, "education", []) or []
    projects_list = getattr(parsed, "projects", []) or []
    experience_list = getattr(parsed, "experience", []) or []
    skills_list = getattr(parsed, "skills", []) or []
    socials_list = getattr(parsed, "socials", []) or []
    achievements_list = getattr(parsed, "achievements", []) or []

    onboarding_doc = {
        "name": name,
        "education": " | ".join(education_list),
        "projects": " | ".join(projects_list),
        "experience": " | ".join(experience_list),
        "skills": skills_list,
        "socials": socials_list,
    }

    resume_parsed_doc = {
        "fileUrl": file_url,
        "name": name,
        "extractedSkills": skills_list,
        "projects": projects_list,
        "experience": experience_list,
        "education": education_list,
        "achievements": achievements_list,
        "socials": socials_list,
        "lastParsedAt": now,
    }

    resume_generated_doc = {
        "fileUrl": file_url,
        "name": name,
        "generatedAt": now,
    }

    return onboarding_doc, resume_parsed_doc, resume_generated_doc
