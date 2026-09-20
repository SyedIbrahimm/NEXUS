from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from pypdf import PdfReader
from docx import Document

from pdf2image import convert_from_bytes
import pytesseract

import io
import re


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="NEXUS AI Engine",
    description="AI Career & Skill Intelligence Platform",
    version="1.0.0"
)


# =========================================================
# TESSERACT OCR CONFIGURATION
# =========================================================

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# =========================================================
# POPPLER CONFIGURATION
# =========================================================

POPPLER_PATH = (
    r"C:\Users\syedi\Downloads\Release-26.09.0-0"
    r"\poppler-26.09.0\Library\bin"
)


# =========================================================
# SKILLS DATABASE
# =========================================================

SKILLS = {
    "python",
    "java",
    "c",
    "c++",
    "sql",
    "mongodb",
    "mysql",

    "html",
    "css",
    "javascript",
    "react",
    "node.js",
    "express.js",

    "fastapi",
    "django",
    "spring boot",
    "rest api",

    "git",
    "github",

    "docker",
    "kubernetes",

    "aws",
    "azure",
    "gcp",
    "linux",

    "machine learning",
    "deep learning",
    "data science"
}


# =========================================================
# JOB ROLES
# =========================================================

JOB_ROLES = {

    "Python Developer": {
        "required": {
            "python",
            "fastapi",
            "sql",
            "git",
            "docker"
        }
    },

    "Java Developer": {
        "required": {
            "java",
            "sql",
            "git",
            "spring boot",
            "rest api"
        }
    },

    "Backend Developer": {
        "required": {
            "python",
            "mongodb",
            "rest api",
            "git",
            "docker"
        }
    },

    "Frontend Developer": {
        "required": {
            "html",
            "css",
            "javascript",
            "react",
            "git"
        }
    },

    "Full Stack Developer": {
        "required": {
            "html",
            "css",
            "javascript",
            "react",
            "node.js",
            "mongodb",
            "git"
        }
    },

    "Cloud Engineer": {
        "required": {
            "aws",
            "linux",
            "docker",
            "kubernetes",
            "git"
        }
    }
}


# =========================================================
# REQUEST MODEL
# =========================================================

class SkillRequest(BaseModel):
    skills: list[str]


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "message": "NEXUS AI Engine is running",
        "status": "success"
    }


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize_text(text: str) -> str:

    text = text.lower()

    replacements = {

        "node js": "node.js",
        "nodejs": "node.js",

        "express js": "express.js",
        "expressjs": "express.js",

        "restful api": "rest api",
        "restful apis": "rest api",
        "rest apis": "rest api",

        "springboot": "spring boot",

        "machine-learning": "machine learning",
        "machinelearning": "machine learning",

        "deep-learning": "deep learning",
        "deeplearning": "deep learning",

        "data-science": "data science",
        "datascience": "data science"
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


# =========================================================
# SKILL DETECTION
# =========================================================

def detect_skills(text: str):

    text = normalize_text(text)

    detected = []

    for skill in SKILLS:

        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text):
            detected.append(skill)

    return sorted(detected)


# =========================================================
# ROLE RECOMMENDATION CALCULATION
# =========================================================

def calculate_recommendations(skill_set):

    recommendations = []

    for role, data in JOB_ROLES.items():

        required = data["required"]

        matched = skill_set.intersection(required)

        missing = required - skill_set

        if len(required) > 0:
            score = round(
                (len(matched) / len(required)) * 100
            )
        else:
            score = 0

        recommendations.append({

            "role": role,

            "match_percentage": score,

            "matched_skills": sorted(matched),

            "missing_skills": sorted(missing)
        })

    recommendations.sort(
        key=lambda x: x["match_percentage"],
        reverse=True
    )

    return recommendations


# =========================================================
# ANALYZE SKILLS API
# =========================================================

@app.post("/analyze-skills")
def analyze_skills(request: SkillRequest):

    skills = {
        skill.lower().strip()
        for skill in request.skills
    }

    recommendations = calculate_recommendations(
        skills
    )

    if recommendations:

        best_role = recommendations[0]

    else:

        best_role = {
            "role": "No suitable role found",
            "match_percentage": 0
        }

    return {

        "detected_skills": sorted(skills),

        "best_role": best_role["role"],

        "best_match_percentage":
            best_role["match_percentage"],

        "recommendations":
            recommendations
    }


# =========================================================
# PDF TEXT EXTRACTION
# =========================================================

def extract_pdf_text(file_bytes):

    pdf = PdfReader(
        io.BytesIO(file_bytes)
    )

    text = ""

    # -----------------------------------------------------
    # FIRST: TRY NORMAL PDF TEXT EXTRACTION
    # -----------------------------------------------------

    for page_number, page in enumerate(pdf.pages):

        page_text = page.extract_text()

        print(
            f"\n----- PDF PAGE {page_number + 1} -----"
        )

        if page_text:

            print(page_text)

            text += page_text + "\n"

        else:

            print(
                "No text extracted from this page."
            )

    # -----------------------------------------------------
    # SECOND: OCR FALLBACK
    # -----------------------------------------------------

    if not text.strip():

        print("\n================================")
        print("NO TEXT LAYER FOUND")
        print("STARTING OCR...")
        print("================================\n")

        images = convert_from_bytes(

            file_bytes,

            dpi=200,

            poppler_path=POPPLER_PATH
        )

        for page_number, image in enumerate(images):

            print(
                f"\n----- OCR PAGE {page_number + 1} -----"
            )

            ocr_text = pytesseract.image_to_string(

                image,

                config="--psm 6"
            )

            print(ocr_text)

            text += ocr_text + "\n"

    # -----------------------------------------------------
    # FINAL DEBUG
    # -----------------------------------------------------

    print(
        "\n----- EXTRACTED RESUME TEXT -----"
    )

    print(text)

    print(
        "\n----- END RESUME TEXT -----"
    )

    return text


# =========================================================
# DOCX TEXT EXTRACTION
# =========================================================

def extract_docx_text(file_bytes):

    document = Document(
        io.BytesIO(file_bytes)
    )

    text = ""

    for paragraph in document.paragraphs:

        text += paragraph.text + "\n"

    print(
        "\n----- DOCX EXTRACTED TEXT -----"
    )

    print(text)

    print(
        "\n----- END DOCX TEXT -----"
    )

    return text


# =========================================================
# ANALYZE RESUME API
# =========================================================

@app.post("/analyze-resume")
async def analyze_resume(
    file: UploadFile = File(...)
):

    # -----------------------------------------------------
    # READ FILE
    # -----------------------------------------------------

    file_bytes = await file.read()

    filename = file.filename.lower()

    print(
        f"\nAnalyzing file: {file.filename}"
    )

    # -----------------------------------------------------
    # PDF
    # -----------------------------------------------------

    if filename.endswith(".pdf"):

        resume_text = extract_pdf_text(
            file_bytes
        )

    # -----------------------------------------------------
    # DOCX
    # -----------------------------------------------------

    elif filename.endswith(".docx"):

        resume_text = extract_docx_text(
            file_bytes
        )

    # -----------------------------------------------------
    # UNSUPPORTED FILE
    # -----------------------------------------------------

    else:

        return {

            "status": "error",

            "message":
                "Only PDF and DOCX files are supported"
        }

    # -----------------------------------------------------
    # EMPTY TEXT CHECK
    # -----------------------------------------------------

    if not resume_text.strip():

        return {

            "status": "error",

            "filename": file.filename,

            "detected_skills": [],

            "message":
                "Could not extract text from the resume."
        }

    # -----------------------------------------------------
    # DETECT SKILLS
    # -----------------------------------------------------

    detected_skills = detect_skills(
        resume_text
    )

    print(
        "\nDetected Skills:"
    )

    print(
        detected_skills
    )

    # -----------------------------------------------------
    # CREATE SKILL SET
    # -----------------------------------------------------

    skill_set = set(
        detected_skills
    )

    # -----------------------------------------------------
    # CALCULATE RECOMMENDATIONS
    # -----------------------------------------------------

    recommendations = calculate_recommendations(
        skill_set
    )

    # -----------------------------------------------------
    # BEST ROLE
    # -----------------------------------------------------

    if recommendations:

        best_role = recommendations[0]

    else:

        best_role = {

            "role":
                "No suitable role found",

            "match_percentage":
                0
        }

    # -----------------------------------------------------
    # FINAL RESPONSE
    # -----------------------------------------------------

    return {

        "filename":
            file.filename,

        "detected_skills":
            detected_skills,

        "best_role":
            best_role["role"],

        "best_match_percentage":
            best_role["match_percentage"],

        "recommendations":
            recommendations,

        "message":
            "Resume analysis completed successfully"
    }