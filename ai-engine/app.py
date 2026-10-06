from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from pypdf import PdfReader
from docx import Document
from pdf2image import convert_from_bytes
import pytesseract
import io
import re
import os
from typing import Dict, List


# ============================================================
# NEXUS AI CAREER & SKILL INTELLIGENCE PLATFORM
# V4.0 - Premium UI
# ============================================================

app = FastAPI(
    title="NEXUS AI Career & Skill Intelligence Platform",
    version="4.0.0",
    description="AI-powered resume analysis and career intelligence platform"
)


# ============================================================
# CONFIGURATION
# ============================================================

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

POPPLER_PATH = (
    r"C:\Users\syedi\Downloads\Release-26.09.0-0"
    r"\poppler-26.09.0\Library\bin"
)

if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


# ============================================================
# SKILLS
# ============================================================

SKILLS = [
    "python", "java", "c", "c++", "c#", "javascript", "typescript",
    "html", "css", "bootstrap", "tailwind css", "react",
    "node.js", "express", "fastapi", "rest api",
    "sql", "mysql", "postgresql", "mongodb",
    "git", "github", "postman", "linux", "vs code",
    "aws", "azure", "gcp", "cloud computing",
    "docker", "kubernetes", "devops", "ci/cd",
    "machine learning", "deep learning", "data science",
    "numpy", "pandas", "tensorflow", "pytorch",
    "artificial intelligence", "ai",
    "figma", "firebase"
]


SKILL_CATEGORIES = {
    "Programming": [
        "python", "java", "c", "c++", "c#", "javascript", "typescript"
    ],

    "Frontend": [
        "html", "css", "bootstrap", "tailwind css", "react", "javascript"
    ],

    "Backend": [
        "python", "java", "node.js", "express", "fastapi", "rest api"
    ],

    "Database": [
        "sql", "mysql", "postgresql", "mongodb", "firebase"
    ],

    "Cloud": [
        "aws", "azure", "gcp", "cloud computing"
    ],

    "DevOps": [
        "docker", "kubernetes", "devops", "ci/cd", "linux", "git"
    ],

    "AI / ML": [
        "machine learning",
        "deep learning",
        "data science",
        "numpy",
        "pandas",
        "tensorflow",
        "pytorch",
        "artificial intelligence",
        "ai"
    ],

    "Tools": [
        "git", "github", "postman", "vs code", "figma"
    ]
}


# ============================================================
# CAREER ROLES
# ============================================================

ROLES = {
    "Python Developer": [
        "python", "fastapi", "django", "sql", "git"
    ],

    "Java Developer": [
        "java", "sql", "git", "rest api"
    ],

    "Backend Developer": [
        "python", "node.js", "rest api", "mongodb", "sql", "git"
    ],

    "Frontend Developer": [
        "html", "css", "javascript", "react", "bootstrap"
    ],

    "Full Stack Developer": [
        "html", "css", "javascript", "react",
        "node.js", "mongodb", "sql"
    ],

    "Cloud Engineer": [
        "aws", "linux", "docker", "kubernetes", "git"
    ],

    "DevOps Engineer": [
        "aws", "docker", "kubernetes", "linux", "git", "devops"
    ],

    "Data Scientist": [
        "python", "pandas", "numpy",
        "machine learning", "sql"
    ],

    "Machine Learning Engineer": [
        "python",
        "machine learning",
        "deep learning",
        "numpy",
        "pandas"
    ]
}


LEARNING_MAP = {
    "react": "Learn React and modern frontend development",
    "docker": "Master Docker containerization",
    "kubernetes": "Learn Kubernetes fundamentals",
    "aws": "Strengthen AWS cloud architecture",
    "linux": "Improve Linux administration skills",
    "git": "Master Git and GitHub workflows",
    "sql": "Improve advanced SQL and database design",
    "mongodb": "Learn MongoDB data modeling",
    "machine learning": "Build practical Machine Learning projects",
    "python": "Strengthen Python programming and backend development",
    "rest api": "Learn REST API design and authentication",
    "devops": "Build CI/CD and DevOps automation skills"
}


# ============================================================
# TEXT EXTRACTION
# ============================================================

def extract_pdf_text(file_bytes: bytes) -> str:

    text = ""

    try:
        reader = PdfReader(io.BytesIO(file_bytes))

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    except Exception:
        pass

    # OCR fallback
    if len(text.strip()) < 80:

        try:
            images = convert_from_bytes(
                file_bytes,
                poppler_path=POPPLER_PATH
            )

            ocr_text = []

            for image in images:
                ocr_text.append(
                    pytesseract.image_to_string(image)
                )

            text = "\n".join(ocr_text)

        except Exception:
            pass

    return text


def extract_docx_text(file_bytes: bytes) -> str:

    document = Document(io.BytesIO(file_bytes))

    paragraphs = [
        p.text.strip()
        for p in document.paragraphs
        if p.text.strip()
    ]

    return "\n".join(paragraphs)


def extract_text(filename: str, file_bytes: bytes) -> str:

    extension = filename.lower().split(".")[-1]

    if extension == "pdf":
        return extract_pdf_text(file_bytes)

    if extension == "docx":
        return extract_docx_text(file_bytes)

    raise HTTPException(
        status_code=400,
        detail="Only PDF and DOCX files are supported."
    )


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_text(text: str) -> str:

    text = text.lower()

    replacements = {
        "node js": "node.js",
        "nodejs": "node.js",
        "restful api": "rest api",
        "amazon web services": "aws",
        "machine-learning": "machine learning",
        "deep-learning": "deep learning",
        "tailwindcss": "tailwind css"
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


# ============================================================
# SKILL DETECTION
# ============================================================

def detect_skills(text: str) -> List[str]:

    normalized = normalize_text(text)

    found = []

    for skill in SKILLS:

        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"

        if re.search(pattern, normalized):

            if skill not in found:
                found.append(skill)

    return sorted(found)


# ============================================================
# CATEGORY MAPPING
# ============================================================

def categorize_skills(skills: List[str]) -> Dict[str, List[str]]:

    result = {}

    for category, category_skills in SKILL_CATEGORIES.items():

        matched = [
            skill
            for skill in category_skills
            if skill in skills
        ]

        if matched:
            result[category] = sorted(set(matched))

    return result


# ============================================================
# ROLE MATCHING
# ============================================================

def calculate_role_matches(skills: List[str]):

    results = []

    skill_set = set(skills)

    for role, required_skills in ROLES.items():

        matched = [
            skill
            for skill in required_skills
            if skill in skill_set
        ]

        missing = [
            skill
            for skill in required_skills
            if skill not in skill_set
        ]

        percentage = round(
            (len(matched) / len(required_skills)) * 100
        )

        results.append({
            "role": role,
            "match_percentage": percentage,
            "matched_skills": matched,
            "missing_skills": missing
        })

    results.sort(
        key=lambda x: x["match_percentage"],
        reverse=True
    )

    return results


# ============================================================
# PERSONAL INFORMATION
# ============================================================

def extract_email(text: str):

    match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )

    return match.group(0) if match else ""


def extract_phone(text: str):

    match = re.search(
        r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)",
        text
    )

    return match.group(0) if match else ""


def extract_name(text: str):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    ignored = {
        "resume",
        "curriculum vitae",
        "professional summary",
        "summary",
        "education",
        "experience",
        "projects",
        "skills",
        "certifications",
        "contact"
    }

    for line in lines[:15]:

        clean = re.sub(
            r"[^A-Za-z .'-]",
            "",
            line
        ).strip()

        words = clean.split()

        if (
            2 <= len(words) <= 5
            and clean.lower() not in ignored
            and "@" not in line
            and not re.search(r"\d", line)
            and len(clean) >= 5
        ):

            # Avoid sentence fragments
            if not clean.endswith("."):

                return clean.title()

    return ""


# ============================================================
# SECTION EXTRACTION
# ============================================================

SECTION_ALIASES = {

    "education": [
        "education",
        "academic background",
        "educational qualification"
    ],

    "experience": [
        "experience",
        "work experience",
        "internship",
        "internships"
    ],

    "projects": [
        "projects",
        "project"
    ],

    "certifications": [
        "certifications",
        "certificates",
        "courses"
    ]
}


def extract_sections(text: str):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    sections = {
        "education": "",
        "experience": "",
        "projects": "",
        "certifications": ""
    }

    current = None

    for line in lines:

        lower = line.lower()

        detected_section = None

        for section, aliases in SECTION_ALIASES.items():

            if any(
                lower == alias
                or lower.startswith(alias + ":")
                for alias in aliases
            ):
                detected_section = section
                break

        if detected_section:

            current = detected_section
            continue

        if current:

            sections[current] += line + "\n"

    return {
        key: value.strip()
        for key, value in sections.items()
    }


# ============================================================
# ATS SCORE
# ============================================================

def calculate_ats_score(
    text: str,
    skills: List[str],
    sections: Dict[str, str]
):

    score = 0

    # Skill coverage
    if len(skills) >= 20:
        score += 35
    elif len(skills) >= 12:
        score += 28
    elif len(skills) >= 7:
        score += 20
    elif len(skills) >= 4:
        score += 12
    else:
        score += 5

    # Contact details
    if extract_email(text):
        score += 10

    if extract_phone(text):
        score += 10

    # Sections
    section_count = sum(
        1 for value in sections.values()
        if value.strip()
    )

    score += min(section_count * 7, 28)

    # Resume length/content
    word_count = len(text.split())

    if word_count >= 350:
        score += 12
    elif word_count >= 200:
        score += 8
    elif word_count >= 100:
        score += 4

    return min(score, 100)


# ============================================================
# LEARNING RECOMMENDATIONS
# ============================================================

def get_learning_recommendations(
    best_role,
    best_missing
):

    recommendations = []

    for skill in best_missing:

        if skill in LEARNING_MAP:

            recommendations.append({
                "skill": skill,
                "recommendation": LEARNING_MAP[skill]
            })

    return recommendations[:6]


# ============================================================
# RESUME ANALYSIS
# ============================================================

def analyze_resume(filename: str, text: str):

    skills = detect_skills(text)

    categories = categorize_skills(skills)

    role_matches = calculate_role_matches(skills)

    sections = extract_sections(text)

    best_role_data = role_matches[0]

    ats_score = calculate_ats_score(
        text,
        skills,
        sections
    )

    learning = get_learning_recommendations(
        best_role_data["role"],
        best_role_data["missing_skills"]
    )

    return {

        "status": "success",

        "filename": filename,

        "resume_information": {
            "name": extract_name(text),
            "email": extract_email(text),
            "phone": extract_phone(text),
            "education": sections["education"],
            "experience": sections["experience"],
            "projects": sections["projects"],
            "certifications": sections["certifications"]
        },

        "detected_skills": skills,

        "skill_categories": categories,

        "ats_score": ats_score,

        "best_role": best_role_data["role"],

        "best_match_percentage":
            best_role_data["match_percentage"],

        "matched_skills":
            best_role_data["matched_skills"],

        "missing_skills":
            best_role_data["missing_skills"],

        "top_roles":
            role_matches[:5],

        "learning_recommendations":
            learning,

        "message":
            "Resume analysis completed successfully"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "NEXUS AI Engine",
        "version": "4.0.0"
    }


# ============================================================
# API
# ============================================================

@app.post("/analyze-resume")
async def analyze_resume_endpoint(
    file: UploadFile = File(...)
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )

    extension = file.filename.lower().split(".")[-1]

    if extension not in ["pdf", "docx"]:

        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported."
        )

    file_bytes = await file.read()

    if len(file_bytes) > 10 * 1024 * 1024:

        raise HTTPException(
            status_code=400,
            detail="File size must be below 10 MB."
        )

    text = extract_text(
        file.filename,
        file_bytes
    )

    if not text.strip():

        raise HTTPException(
            status_code=422,
            detail="Could not extract readable text from the resume."
        )

    return analyze_resume(
        file.filename,
        text
    )


@app.post("/analyze-skills")
async def analyze_skills_endpoint(
    file: UploadFile = File(...)
):

    file_bytes = await file.read()

    text = extract_text(
        file.filename,
        file_bytes
    )

    skills = detect_skills(text)

    return {
        "status": "success",
        "skills": skills,
        "categories": categorize_skills(skills)
    }


# ============================================================
# PREMIUM NEXUS UI
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def home():

    return HTMLResponse("""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>NEXUS — AI Career Intelligence</title>

<style>

*{
    margin:0;
    padding:0;
    box-sizing:border-box;
}

:root{

    --bg:#050816;
    --bg2:#0a1025;
    --card:rgba(16,24,48,.72);
    --border:rgba(255,255,255,.09);
    --text:#f8fafc;
    --muted:#94a3b8;
    --primary:#7c3aed;
    --secondary:#06b6d4;
    --success:#22c55e;
    --danger:#fb7185;
}

body{

    font-family:
        Inter,
        ui-sans-serif,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;

    background:
        radial-gradient(
            circle at 15% 15%,
            rgba(124,58,237,.22),
            transparent 32%
        ),
        radial-gradient(
            circle at 85% 10%,
            rgba(6,182,212,.16),
            transparent 28%
        ),
        linear-gradient(
            135deg,
            #050816,
            #080d20 55%,
            #050816
        );

    color:var(--text);

    min-height:100vh;

    overflow-x:hidden;
}

body::before{

    content:"";

    position:fixed;

    inset:0;

    pointer-events:none;

    opacity:.18;

    background-image:
        linear-gradient(
            rgba(255,255,255,.025) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(255,255,255,.025) 1px,
            transparent 1px
        );

    background-size:50px 50px;
}

.container{

    width:min(1180px,92%);

    margin:auto;
}


/* NAVBAR */

nav{

    height:82px;

    display:flex;

    align-items:center;

    justify-content:space-between;

    border-bottom:1px solid var(--border);

    position:relative;

    z-index:5;
}

.logo{

    display:flex;

    align-items:center;

    gap:12px;

    font-size:22px;

    font-weight:800;

    letter-spacing:-.5px;
}

.logo-mark{

    width:38px;

    height:38px;

    border-radius:12px;

    display:grid;

    place-items:center;

    background:
        linear-gradient(
            135deg,
            var(--primary),
            var(--secondary)
        );

    box-shadow:
        0 0 30px rgba(124,58,237,.35);
}

.logo-mark::after{

    content:"N";

    font-weight:900;

    color:white;
}

.nav-links{

    display:flex;

    gap:30px;

    color:var(--muted);

    font-size:14px;
}

.nav-links span{

    cursor:pointer;

    transition:.2s;
}

.nav-links span:hover{

    color:white;
}

.nav-badge{

    padding:9px 14px;

    border:1px solid var(--border);

    border-radius:999px;

    color:#c4b5fd;

    background:rgba(124,58,237,.08);

    font-size:12px;

    font-weight:600;
}


/* HERO */

.hero{

    text-align:center;

    padding:92px 0 55px;

}

.eyebrow{

    display:inline-flex;

    align-items:center;

    gap:8px;

    padding:8px 14px;

    border-radius:999px;

    border:1px solid rgba(124,58,237,.35);

    background:rgba(124,58,237,.08);

    color:#c4b5fd;

    font-size:12px;

    font-weight:700;

    letter-spacing:.5px;

    text-transform:uppercase;
}

.dot{

    width:7px;

    height:7px;

    border-radius:50%;

    background:#22c55e;

    box-shadow:0 0 12px #22c55e;
}

.hero h1{

    font-size:clamp(42px,7vw,78px);

    line-height:.98;

    letter-spacing:-4px;

    margin:26px auto 22px;

    max-width:900px;
}

.gradient-text{

    background:
        linear-gradient(
            100deg,
            #fff,
            #c4b5fd 45%,
            #67e8f9
        );

    -webkit-background-clip:text;

    color:transparent;
}

.hero p{

    max-width:650px;

    margin:auto;

    color:var(--muted);

    font-size:18px;

    line-height:1.7;
}


/* UPLOAD */

.upload-section{

    max-width:820px;

    margin:25px auto 90px;
}

.upload-card{

    position:relative;

    padding:45px;

    border-radius:28px;

    border:1px solid var(--border);

    background:
        linear-gradient(
            145deg,
            rgba(18,27,55,.86),
            rgba(8,14,31,.86)
        );

    box-shadow:
        0 30px 100px rgba(0,0,0,.35),
        inset 0 1px 0 rgba(255,255,255,.04);

    backdrop-filter:blur(20px);

    overflow:hidden;
}

.upload-card::before{

    content:"";

    position:absolute;

    width:250px;

    height:250px;

    background:rgba(124,58,237,.18);

    filter:blur(80px);

    top:-120px;

    left:-80px;
}

.drop-zone{

    border:1.5px dashed rgba(148,163,184,.25);

    border-radius:22px;

    padding:55px 25px;

    text-align:center;

    transition:.3s;

    position:relative;

    cursor:pointer;
}

.drop-zone:hover,
.drop-zone.dragover{

    border-color:#8b5cf6;

    background:rgba(124,58,237,.07);

    transform:translateY(-2px);
}

.upload-icon{

    width:72px;

    height:72px;

    margin:0 auto 20px;

    border-radius:22px;

    display:grid;

    place-items:center;

    font-size:30px;

    background:
        linear-gradient(
            135deg,
            rgba(124,58,237,.25),
            rgba(6,182,212,.18)
        );

    border:1px solid rgba(255,255,255,.08);
}

.drop-zone h3{

    font-size:21px;

    margin-bottom:9px;
}

.drop-zone p{

    color:var(--muted);

    font-size:14px;

    margin-bottom:23px;
}

.file-input{

    display:none;
}

.choose-btn{

    display:inline-flex;

    padding:13px 22px;

    border-radius:12px;

    background:white;

    color:#080816;

    font-weight:800;

    font-size:14px;

    cursor:pointer;

    transition:.2s;
}

.choose-btn:hover{

    transform:translateY(-2px);

    box-shadow:0 10px 30px rgba(255,255,255,.12);
}

.file-name{

    display:none;

    margin-top:20px;

    color:#c4b5fd;

    font-size:14px;

    font-weight:600;
}

.analyze-btn{

    width:100%;

    margin-top:18px;

    padding:16px;

    border:none;

    border-radius:14px;

    cursor:pointer;

    color:white;

    font-size:15px;

    font-weight:800;

    background:
        linear-gradient(
            100deg,
            #7c3aed,
            #2563eb,
            #06b6d4
        );

    box-shadow:
        0 15px 35px rgba(79,70,229,.25);

    transition:.25s;

    display:none;
}

.analyze-btn:hover{

    transform:translateY(-2px);

    box-shadow:
        0 20px 45px rgba(79,70,229,.35);
}

.analyze-btn:disabled{

    opacity:.6;

    cursor:not-allowed;

    transform:none;
}


/* FEATURES */

.features{

    display:grid;

    grid-template-columns:
        repeat(3,1fr);

    gap:18px;

    margin-bottom:80px;
}

.feature{

    padding:24px;

    border-radius:20px;

    border:1px solid var(--border);

    background:rgba(15,23,42,.55);
}

.feature-icon{

    font-size:22px;

    margin-bottom:15px;
}

.feature h4{

    margin-bottom:7px;
}

.feature p{

    color:var(--muted);

    font-size:13px;

    line-height:1.6;
}


/* RESULTS */

.results{

    display:none;

    padding-bottom:90px;
}

.results-header{

    display:flex;

    justify-content:space-between;

    align-items:flex-end;

    margin-bottom:25px;
}

.results-header h2{

    font-size:32px;

    letter-spacing:-1px;
}

.results-header p{

    color:var(--muted);

    margin-top:5px;
}

.new-analysis{

    border:1px solid var(--border);

    background:rgba(255,255,255,.04);

    color:white;

    padding:10px 16px;

    border-radius:10px;

    cursor:pointer;
}


/* SCORE CARDS */

.stats{

    display:grid;

    grid-template-columns:
        1.2fr 1fr 1fr;

    gap:18px;

    margin-bottom:18px;
}

.stat-card{

    padding:27px;

    min-height:175px;

    border-radius:22px;

    border:1px solid var(--border);

    background:
        linear-gradient(
            145deg,
            rgba(17,25,50,.85),
            rgba(10,15,31,.75)
        );

    position:relative;

    overflow:hidden;
}

.stat-card::after{

    content:"";

    position:absolute;

    width:130px;

    height:130px;

    border-radius:50%;

    background:rgba(124,58,237,.12);

    filter:blur(40px);

    right:-50px;

    top:-50px;
}

.stat-label{

    color:var(--muted);

    font-size:12px;

    text-transform:uppercase;

    letter-spacing:1px;

    font-weight:700;
}

.score-row{

    display:flex;

    align-items:center;

    gap:20px;

    margin-top:15px;
}

.score-circle{

    width:92px;

    height:92px;

    border-radius:50%;

    display:grid;

    place-items:center;

    background:
        conic-gradient(
            #8b5cf6 var(--score),
            rgba(255,255,255,.07) 0
        );

    position:relative;
}

.score-circle::before{

    content:"";

    position:absolute;

    inset:7px;

    border-radius:50%;

    background:#0b1228;
}

.score-number{

    position:relative;

    font-size:23px;

    font-weight:900;
}

.stat-card h3{

    margin-top:14px;

    font-size:24px;
}


/* CONTENT GRID */

.content-grid{

    display:grid;

    grid-template-columns:
        1.4fr .8fr;

    gap:18px;

    margin-top:18px;
}

.panel{

    padding:26px;

    border-radius:22px;

    border:1px solid var(--border);

    background:rgba(12,19,40,.72);
}

.panel-title{

    display:flex;

    justify-content:space-between;

    align-items:center;

    margin-bottom:20px;
}

.panel-title h3{

    font-size:18px;
}

.panel-title span{

    color:var(--muted);

    font-size:12px;
}


/* SKILLS */

.skill-group{

    margin-bottom:20px;
}

.skill-group:last-child{

    margin-bottom:0;
}

.skill-group-title{

    color:#cbd5e1;

    font-size:12px;

    font-weight:700;

    margin-bottom:10px;
}

.skill-list{

    display:flex;

    flex-wrap:wrap;

    gap:8px;
}

.skill{

    padding:8px 11px;

    border-radius:9px;

    background:rgba(124,58,237,.10);

    border:1px solid rgba(124,58,237,.20);

    color:#ddd6fe;

    font-size:12px;

    font-weight:600;
}


/* ROLE LIST */

.role{

    padding:16px 0;

    border-bottom:1px solid var(--border);
}

.role:last-child{

    border-bottom:none;
}

.role-top{

    display:flex;

    justify-content:space-between;

    margin-bottom:9px;
}

.role-name{

    font-weight:700;

    font-size:14px;
}

.role-percent{

    color:#a78bfa;

    font-weight:800;

    font-size:13px;
}

.bar{

    height:7px;

    border-radius:20px;

    background:rgba(255,255,255,.06);

    overflow:hidden;
}

.bar-fill{

    height:100%;

    border-radius:20px;

    background:
        linear-gradient(
            90deg,
            #7c3aed,
            #06b6d4
        );
}


/* MISSING */

.missing-list{

    display:flex;

    flex-wrap:wrap;

    gap:9px;
}

.missing{

    padding:9px 12px;

    border-radius:10px;

    background:rgba(251,113,133,.08);

    border:1px solid rgba(251,113,133,.18);

    color:#fda4af;

    font-size:12px;

    font-weight:600;
}


/* LEARNING */

.learning{

    display:grid;

    grid-template-columns:
        repeat(2,1fr);

    gap:12px;
}

.learning-card{

    padding:16px;

    border-radius:15px;

    background:rgba(255,255,255,.035);

    border:1px solid var(--border);
}

.learning-card strong{

    display:block;

    color:#c4b5fd;

    margin-bottom:7px;
}

.learning-card p{

    color:var(--muted);

    font-size:12px;

    line-height:1.5;
}


/* PROFILE */

.profile{

    display:grid;

    grid-template-columns:
        repeat(3,1fr);

    gap:12px;
}

.profile-item{

    padding:15px;

    border-radius:13px;

    background:rgba(255,255,255,.035);
}

.profile-label{

    color:var(--muted);

    font-size:10px;

    text-transform:uppercase;

    letter-spacing:.8px;

    margin-bottom:6px;
}

.profile-value{

    font-size:13px;

    font-weight:700;

    word-break:break-word;
}


/* LOADER */

.loader{

    display:none;

    text-align:center;

    padding:35px;
}

.spinner{

    width:38px;

    height:38px;

    border:3px solid rgba(255,255,255,.1);

    border-top-color:#8b5cf6;

    border-radius:50%;

    animation:spin .8s linear infinite;

    margin:0 auto 15px;
}

@keyframes spin{

    to{
        transform:rotate(360deg);
    }
}


/* FOOTER */

footer{

    border-top:1px solid var(--border);

    padding:28px 0;

    color:var(--muted);

    text-align:center;

    font-size:12px;
}


/* RESPONSIVE */

@media(max-width:850px){

    .nav-links{
        display:none;
    }

    .hero{
        padding-top:65px;
    }

    .hero h1{
        letter-spacing:-2px;
    }

    .features,
    .stats,
    .content-grid{
        grid-template-columns:1fr;
    }

    .profile,
    .learning{
        grid-template-columns:1fr;
    }

    .upload-card{
        padding:20px;
    }

    .drop-zone{
        padding:40px 15px;
    }

    .results-header{
        align-items:flex-start;
        gap:15px;
        flex-direction:column;
    }
}

</style>

</head>


<body>


<div class="container">

<nav>

    <div class="logo">

        <div class="logo-mark"></div>

        NEXUS

    </div>

    <div class="nav-links">

        <span>AI Analysis</span>
        <span>Career Intelligence</span>
        <span>Skill Roadmap</span>

    </div>

    <div class="nav-badge">

        AI POWERED

    </div>

</nav>


<!-- HERO -->

<section class="hero">

    <div class="eyebrow">

        <span class="dot"></span>

        AI Career Intelligence Platform

    </div>


    <h1>

        Turn your resume into

        <span class="gradient-text">
            your career roadmap.
        </span>

    </h1>


    <p>

        NEXUS analyzes your resume, discovers your skills,
        measures ATS readiness and identifies the career
        paths that fit you best.

    </p>

</section>


<!-- UPLOAD -->

<section class="upload-section">

<div class="upload-card">

    <div
        class="drop-zone"
        id="dropZone"
        onclick="document.getElementById('fileInput').click()"
    >

        <div class="upload-icon">
            ↑
        </div>

        <h3>
            Upload your resume
        </h3>

        <p>
            Drag & drop your resume here or choose a file
        </p>

        <label
            class="choose-btn"
            onclick="event.stopPropagation()"
        >

            Choose Resume

            <input
                id="fileInput"
                class="file-input"
                type="file"
                accept=".pdf,.docx"
                onchange="fileSelected()"
            >

        </label>

        <div
            id="fileName"
            class="file-name"
        ></div>

    </div>


    <button
        id="analyzeBtn"
        class="analyze-btn"
        onclick="analyzeResume()"
    >

        ✦ Analyze Resume with NEXUS AI

    </button>


    <div
        id="loader"
        class="loader"
    >

        <div class="spinner"></div>

        <p>
            NEXUS AI is analyzing your resume...
        </p>

    </div>

</div>

</section>


<!-- FEATURES -->

<section class="features">

    <div class="feature">

        <div class="feature-icon">◈</div>

        <h4>ATS Intelligence</h4>

        <p>
            Measure your resume's ATS readiness
            and identify areas that can be improved.
        </p>

    </div>


    <div class="feature">

        <div class="feature-icon">✦</div>

        <h4>Career Matching</h4>

        <p>
            Discover the roles that best match
            your current technical skill set.
        </p>

    </div>


    <div class="feature">

        <div class="feature-icon">↗</div>

        <h4>Skill Roadmap</h4>

        <p>
            Find missing skills and get a focused
            learning roadmap for your target role.
        </p>

    </div>

</section>


<!-- RESULTS -->

<section
    id="results"
    class="results"
>

    <div class="results-header">

        <div>

            <h2>
                AI Resume Analysis
            </h2>

            <p>
                Your personalized career intelligence report
            </p>

        </div>

        <button
            class="new-analysis"
            onclick="resetAnalysis()"
        >
            ← New Analysis
        </button>

    </div>


    <!-- STAT CARDS -->

    <div class="stats">


        <div class="stat-card">

            <div class="stat-label">
                ATS Readiness
            </div>

            <div class="score-row">

                <div
                    class="score-circle"
                    id="scoreCircle"
                    style="--score:0%"
                >

                    <span
                        class="score-number"
                        id="atsScore"
                    >
                        0%
                    </span>

                </div>

                <div>

                    <div
                        id="scoreMessage"
                        style="color:#94a3b8;font-size:13px"
                    >
                        Analyzing...
                    </div>

                </div>

            </div>

        </div>


        <div class="stat-card">

            <div class="stat-label">
                Best Career Role
            </div>

            <h3 id="bestRole">
                —
            </h3>

            <div
                style="
                color:#94a3b8;
                font-size:13px;
                margin-top:8px;
                "
            >
                Based on your detected skills
            </div>

        </div>


        <div class="stat-card">

            <div class="stat-label">
                Role Match
            </div>

            <h3 id="roleMatch">
                0%
            </h3>

            <div
                style="
                color:#94a3b8;
                font-size:13px;
                margin-top:8px;
                "
            >
                Compatibility score
            </div>

        </div>

    </div>


    <!-- PROFILE -->

    <div class="panel">

        <div class="panel-title">

            <h3>Resume Profile</h3>

            <span>Extracted information</span>

        </div>

        <div class="profile">

            <div class="profile-item">

                <div class="profile-label">
                    Name
                </div>

                <div
                    class="profile-value"
                    id="name"
                >
                    —
                </div>

            </div>

            <div class="profile-item">

                <div class="profile-label">
                    Email
                </div>

                <div
                    class="profile-value"
                    id="email"
                >
                    —
                </div>

            </div>

            <div class="profile-item">

                <div class="profile-label">
                    Phone
                </div>

                <div
                    class="profile-value"
                    id="phone"
                >
                    —
                </div>

            </div>

        </div>

    </div>


    <div class="content-grid">


        <!-- SKILLS -->

        <div class="panel">

            <div class="panel-title">

                <h3>
                    Detected Skills
                </h3>

                <span id="skillCount">
                    0 skills
                </span>

            </div>

            <div id="skillsContainer"></div>

        </div>


        <!-- TOP ROLES -->

        <div class="panel">

            <div class="panel-title">

                <h3>
                    Top Career Matches
                </h3>

                <span>
                    AI ranking
                </span>

            </div>

            <div id="rolesContainer"></div>

        </div>

    </div>


    <!-- MISSING SKILLS -->

    <div
        class="panel"
        style="margin-top:18px"
    >

        <div class="panel-title">

            <h3>
                Skills to Develop
            </h3>

            <span>
                Recommended next steps
            </span>

        </div>

        <div
            id="missingSkills"
            class="missing-list"
        ></div>

    </div>


    <!-- LEARNING -->

    <div
        class="panel"
        style="margin-top:18px"
    >

        <div class="panel-title">

            <h3>
                Personalized Learning Roadmap
            </h3>

            <span>
                NEXUS recommendations
            </span>

        </div>

        <div
            id="learningContainer"
            class="learning"
        ></div>

    </div>

</section>


<footer>

    © 2026 NEXUS · AI Career & Skill Intelligence Platform

</footer>

</div>


<script>


const fileInput =
    document.getElementById("fileInput");

const fileName =
    document.getElementById("fileName");

const analyzeBtn =
    document.getElementById("analyzeBtn");

const dropZone =
    document.getElementById("dropZone");

const loader =
    document.getElementById("loader");



function fileSelected(){

    const file = fileInput.files[0];

    if(!file){
        return;
    }

    fileName.style.display = "block";

    fileName.textContent =
        "✓ " + file.name;

    analyzeBtn.style.display =
        "block";
}



dropZone.addEventListener(
    "dragover",
    function(e){

        e.preventDefault();

        dropZone.classList.add("dragover");

    }
);


dropZone.addEventListener(
    "dragleave",
    function(){

        dropZone.classList.remove("dragover");

    }
);


dropZone.addEventListener(
    "drop",
    function(e){

        e.preventDefault();

        dropZone.classList.remove("dragover");

        const files = e.dataTransfer.files;

        if(files.length){

            fileInput.files = files;

            fileSelected();

        }

    }
);



async function analyzeResume(){

    const file =
        fileInput.files[0];

    if(!file){

        alert("Please select a resume first.");

        return;

    }


    analyzeBtn.disabled = true;

    analyzeBtn.style.display = "none";

    loader.style.display = "block";


    const formData =
        new FormData();

    formData.append(
        "file",
        file
    );


    try{

        const response =
            await fetch(
                "/analyze-resume",
                {
                    method:"POST",
                    body:formData
                }
            );


        const data =
            await response.json();


        if(!response.ok){

            throw new Error(
                data.detail ||
                "Analysis failed"
            );

        }


        displayResults(data);


    }catch(error){

        alert(
            "Analysis failed: " +
            error.message
        );

    }finally{

        loader.style.display = "none";

        analyzeBtn.disabled = false;

    }

}



function displayResults(data){


    document.querySelector(".hero").style.display =
        "none";

    document.querySelector(".upload-section").style.display =
        "none";

    document.querySelector(".features").style.display =
        "none";


    document.getElementById("results").style.display =
        "block";


    /* ATS */

    const score =
        data.ats_score || 0;

    document.getElementById("atsScore").textContent =
        score + "%";

    document.getElementById("scoreCircle").style =
        "--score:" + score + "%";


    let message =
        "Needs improvement";

    if(score >= 80){

        message =
            "Excellent ATS readiness";

    }else if(score >= 60){

        message =
            "Good foundation — room to improve";

    }else if(score >= 40){

        message =
            "Moderate readiness";

    }


    document.getElementById("scoreMessage").textContent =
        message;


    /* ROLE */

    document.getElementById("bestRole").textContent =
        data.best_role || "—";


    document.getElementById("roleMatch").textContent =
        (data.best_match_percentage || 0) + "%";


    /* PROFILE */

    const info =
        data.resume_information || {};


    document.getElementById("name").textContent =
        info.name || "Not detected";

    document.getElementById("email").textContent =
        info.email || "Not detected";

    document.getElementById("phone").textContent =
        info.phone || "Not detected";


    /* SKILLS */

    const skillsContainer =
        document.getElementById("skillsContainer");

    skillsContainer.innerHTML = "";


    const categories =
        data.skill_categories || {};


    Object.entries(categories).forEach(
        ([category, skills]) => {

            const group =
                document.createElement("div");

            group.className =
                "skill-group";


            const title =
                document.createElement("div");

            title.className =
                "skill-group-title";

            title.textContent =
                category;


            const list =
                document.createElement("div");

            list.className =
                "skill-list";


            skills.forEach(skill => {

                const chip =
                    document.createElement("span");

                chip.className =
                    "skill";

                chip.textContent =
                    skill;

                list.appendChild(chip);

            });


            group.appendChild(title);

            group.appendChild(list);

            skillsContainer.appendChild(group);

        }
    );


    document.getElementById("skillCount").textContent =
        (data.detected_skills || []).length +
        " skills detected";


    /* ROLES */

    const rolesContainer =
        document.getElementById("rolesContainer");

    rolesContainer.innerHTML = "";


    (data.top_roles || []).forEach(
        role => {

            const item =
                document.createElement("div");

            item.className =
                "role";


            item.innerHTML = `

                <div class="role-top">

                    <span class="role-name">
                        ${role.role}
                    </span>

                    <span class="role-percent">
                        ${role.match_percentage}%
                    </span>

                </div>

                <div class="bar">

                    <div
                        class="bar-fill"
                        style="
                        width:${role.match_percentage}%
                        "
                    ></div>

                </div>
            `;


            rolesContainer.appendChild(item);

        }
    );


    /* MISSING SKILLS */

    const missing =
        data.missing_skills || [];

    const missingContainer =
        document.getElementById("missingSkills");

    missingContainer.innerHTML = "";


    if(!missing.length){

        missingContainer.innerHTML =
            `<span style="color:#22c55e">
                ✓ No major missing skills detected
            </span>`;

    }else{

        missing.forEach(skill => {

            const item =
                document.createElement("span");

            item.className =
                "missing";

            item.textContent =
                skill;

            missingContainer.appendChild(item);

        });

    }


    /* LEARNING */

    const learningContainer =
        document.getElementById(
            "learningContainer"
        );

    learningContainer.innerHTML = "";


    const learning =
        data.learning_recommendations || [];


    if(!learning.length){

        learningContainer.innerHTML = `

            <div class="learning-card">

                <strong>
                    ✓ Strong Skill Coverage
                </strong>

                <p>
                    Your current skill set already
                    covers the main requirements
                    of your matched career roles.
                </p>

            </div>
        `;

    }else{

        learning.forEach(item => {

            const card =
                document.createElement("div");

            card.className =
                "learning-card";


            card.innerHTML = `

                <strong>
                    ${item.skill}
                </strong>

                <p>
                    ${item.recommendation}
                </p>

            `;


            learningContainer.appendChild(card);

        });

    }


    window.scrollTo({
        top:0,
        behavior:"smooth"
    });

}



function resetAnalysis(){

    document.getElementById("results").style.display =
        "none";

    document.querySelector(".hero").style.display =
        "block";

    document.querySelector(".upload-section").style.display =
        "block";

    document.querySelector(".features").style.display =
        "grid";


    fileInput.value = "";

    fileName.style.display =
        "none";

    analyzeBtn.style.display =
        "none";


    window.scrollTo({
        top:0,
        behavior:"smooth"
    });

}

</script>

</body>

</html>
""")


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )