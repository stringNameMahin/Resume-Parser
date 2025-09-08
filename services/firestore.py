import datetime

def map_to_firestore_schema(parsed_data, file_url):
    now = datetime.datetime.utcnow()

    onboarding_doc = {
        "education": " | ".join(parsed_data.education),
        "experience": " | ".join(parsed_data.experience),
        "skills": parsed_data.skills,
        "interests": parsed_data.interests,
    }

    resume_parsed_doc = {
        "fileUrl": file_url,
        "extractedSkills": parsed_data.skills,
        "experience": parsed_data.experience,
        "education": parsed_data.education,
        "achievements": parsed_data.achievements,
        "lastParsedAt": now,
    }

    resume_generated_doc = {
        "fileUrl": file_url,
        "generatedAt": now,
    }

    return onboarding_doc, resume_parsed_doc, resume_generated_doc
