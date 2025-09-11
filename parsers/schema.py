from pydantic import BaseModel
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate

class ResumeSchema(BaseModel):
    name: str
    education: list[str]
    projects: list[str]
    experience: list[str]
    skills: list[str]
    socials: list[str]
    achievements: list[str]

parser = PydanticOutputParser(pydantic_object=ResumeSchema)

prompt = PromptTemplate(
    template="""
    You are a resume parsing assistant.
    Extract structured information from this resume text:

    {resume_text}

    Return valid JSON in this format:
    {format_instructions}
    name: Name of the person in the resume.
    education: Where the user is studying or has studied in past.
    experience: Previous internships or any work experience performed by user (NOT projects).
    projects: Projects made by the user or contributed in by the user.
    skills: Techincal skills, lingual skills, soft skills.
    socials: List of all the social media links given in the resume.
    achievements: Past achievements achieved by the user. Like prices, medals, hackathons wins
    """,
    input_variables=["resume_text"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)
