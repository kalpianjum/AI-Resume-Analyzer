from flask_cors import CORS
from flask import Flask, request, jsonify
import PyPDF2
import re
from sentence_transformers import SentenceTransformer, util

app = Flask(__name__)
CORS(app)


# =========================================================
# 🤖 LOAD LOCAL AI MODEL
# =========================================================

model = SentenceTransformer("all-MiniLM-L6-v2")


# =========================================================
# 🧠 SKILLS DATABASE
# =========================================================

SKILLS_DB = [
    "python",
    "java",
    "c++",
    "html",
    "css",
    "javascript",
    "react",
    "react js",
    "node",
    "node js",
    "express",
    "mongodb",
    "mysql",
    "sql",
    "flask",
    "django",
    "machine learning",
    "deep learning",
    "data science",
    "docker",
    "aws",
    "git"
]


# =========================================================
# 📄 EXTRACT TEXT FROM PDF
# =========================================================

def extract_text_from_pdf(file):

    reader = PyPDF2.PdfReader(file)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + " "

    return text


# =========================================================
# 🧹 CLEAN TEXT
# =========================================================

def clean(text):

    return re.sub(
        r"[^a-zA-Z0-9+#. ]",
        " ",
        text.lower()
    )


# =========================================================
# 🔎 EXACT SKILL EXTRACTION
# =========================================================

def extract_skills(text):

    found = []

    words = set(text.split())

    for skill in SKILLS_DB:

        skill_parts = skill.split()

        if all(part in words for part in skill_parts):
            found.append(skill)

    return list(set(found))


# =========================================================
# ✂️ SPLIT TEXT INTO SENTENCES
# =========================================================

def get_sentences(text):

    sentences = re.split(
        r"[.!?\n]+",
        text
    )

    sentences = [
        sentence.strip()
        for sentence in sentences
        if len(sentence.strip()) > 15
    ]

    return sentences


# =========================================================
# 🧠 EVIDENCE-BASED SKILL ANALYSIS
# =========================================================

def analyze_skill_evidence(resume_text, job_skills):

    resume_sentences = get_sentences(resume_text)

    results = []

    if not resume_sentences:

        for skill in job_skills:

            results.append({

                "skill": skill,

                "status": "NOT DETECTED",

                "score": 0,

                "evidence": "",

                "message": (
                    f"No clear {skill}-related "
                    "experience was found in the "
                    "submitted resume."
                )

            })

        return results


    # -----------------------------------------------------
    # Create embeddings for resume sentences
    # -----------------------------------------------------

    resume_embeddings = model.encode(
        resume_sentences,
        convert_to_tensor=True
    )


    # -----------------------------------------------------
    # Analyze every required skill
    # -----------------------------------------------------

    for skill in job_skills:

        # -------------------------------------------------
        # First check exact skill mention
        # -------------------------------------------------

        exact_match = False
        exact_evidence = ""

        for sentence in resume_sentences:

            sentence_words = set(
                sentence.lower().split()
            )

            skill_parts = skill.lower().split()

            if all(
                part in sentence_words
                for part in skill_parts
            ):

                exact_match = True
                exact_evidence = sentence
                break


        # -------------------------------------------------
        # Exact match = strong evidence
        # -------------------------------------------------

        if exact_match:

            results.append({

                "skill": skill,

                "status": "MATCH",

                "score": 100,

                "evidence": exact_evidence,

                "message": (
                    f"Clear {skill}-related "
                    "experience was found."
                )

            })

            continue


        # -------------------------------------------------
        # Semantic comparison
        # -------------------------------------------------

        skill_description = (
            f"Professional experience with {skill}. "
            f"Developed projects using {skill}. "
            f"Worked with {skill} in software development."
        )

        skill_embedding = model.encode(
            skill_description,
            convert_to_tensor=True
        )

        similarities = util.cos_sim(
            skill_embedding,
            resume_embeddings
        )[0]

        best_index = int(
            similarities.argmax().item()
        )

        best_score = float(
            similarities[best_index].item()
        )

        best_evidence = resume_sentences[
            best_index
        ]

        score_percentage = int(
            max(
                0,
                min(best_score * 100, 100)
            )
        )


        # -------------------------------------------------
        # Determine evidence status
        # -------------------------------------------------

        if best_score >= 0.55:

            status = "MATCH"

            message = (
                f"Strong semantic evidence "
                f"related to {skill} was found."
            )


        elif best_score >= 0.40:

            status = "PARTIAL MATCH"

            message = (
                f"Related experience was found, "
                f"but the resume does not clearly "
                f"confirm {skill}."
            )


        else:

            status = "NOT DETECTED"

            best_evidence = ""

            score_percentage = 0

            message = (
                f"No clear {skill}-related "
                "experience was found in the "
                "submitted resume."
            )


        results.append({

            "skill": skill,

            "status": status,

            "score": score_percentage,

            "evidence": best_evidence,

            "message": message

        })


    return results


# =========================================================
# 🧠 SEMANTIC JOB REQUIREMENT MATCHING
# =========================================================

def semantic_job_matching(
    resume_text,
    job_desc
):

    resume_sentences = get_sentences(
        resume_text
    )

    job_requirements = get_sentences(
        job_desc
    )

    if not resume_sentences or not job_requirements:

        return []


    resume_embeddings = model.encode(
        resume_sentences,
        convert_to_tensor=True
    )

    job_embeddings = model.encode(
        job_requirements,
        convert_to_tensor=True
    )

    results = []


    for index, requirement in enumerate(
        job_requirements
    ):

        similarities = util.cos_sim(
            job_embeddings[index],
            resume_embeddings
        )[0]

        best_index = int(
            similarities.argmax().item()
        )

        best_score = float(
            similarities[best_index].item()
        )

        evidence = resume_sentences[
            best_index
        ]

        percentage = int(
            max(
                0,
                min(best_score * 100, 100)
            )
        )

        if best_score >= 0.40:

            status = "MATCHED"

        else:

            status = "WEAK / MISSING"


        results.append({

            "requirement": requirement,

            "evidence": evidence,

            "score": percentage,

            "status": status

        })


    return results


# =========================================================
# 💻 TECHNICAL SCORE
# =========================================================

def calculate_technical_score(
    evidence_results
):

    if not evidence_results:

        return 0


    scores = []

    for item in evidence_results:

        scores.append(
            item["score"]
        )


    return int(
        sum(scores) / len(scores)
    )


# =========================================================
# 📁 PROJECT SCORE
# =========================================================

def calculate_project_score(
    resume_text
):

    keywords = [
        "project",
        "projects",
        "built",
        "developed",
        "created",
        "implemented",
        "application",
        "system"
    ]

    matches = sum(
        1
        for keyword in keywords
        if keyword in resume_text
    )

    return min(
        100,
        matches * 20
    )


# =========================================================
# 💼 EXPERIENCE SCORE
# =========================================================

def calculate_experience_score(
    resume_text
):

    keywords = [
        "experience",
        "internship",
        "intern",
        "worked",
        "employment",
        "developer",
        "engineer",
        "software"
    ]

    matches = sum(
        1
        for keyword in keywords
        if keyword in resume_text
    )

    return min(
        100,
        matches * 20
    )


# =========================================================
# ☁️ CLOUD SCORE
# =========================================================

def calculate_cloud_score(
    resume_text,
    job_desc
):

    cloud_keywords = [
        "aws",
        "azure",
        "gcp",
        "cloud",
        "docker",
        "kubernetes"
    ]

    resume_count = sum(
        1
        for keyword in cloud_keywords
        if keyword in resume_text
    )

    job_count = sum(
        1
        for keyword in cloud_keywords
        if keyword in job_desc
    )


    if job_count == 0:

        if resume_count > 0:
            return 100

        return 0


    return int(
        min(
            100,
            (resume_count / job_count) * 100
        )
    )


# =========================================================
# 🗣️ COMMUNICATION SCORE
# =========================================================

def calculate_communication_score(
    resume_text
):

    keywords = [
        "communication",
        "team",
        "teamwork",
        "collaboration",
        "leadership",
        "presentation",
        "presented",
        "managed"
    ]

    matches = sum(
        1
        for keyword in keywords
        if keyword in resume_text
    )

    return min(
        100,
        matches * 20
    )


# =========================================================
# 🎓 EDUCATION SCORE
# =========================================================

def calculate_education_score(
    resume_text
):

    keywords = [
        "education",
        "bachelor",
        "btech",
        "b.sc",
        "bsc",
        "master",
        "m.tech",
        "university",
        "college",
        "degree"
    ]

    matches = sum(
        1
        for keyword in keywords
        if keyword in resume_text
    )


    if matches >= 3:
        return 100

    if matches == 2:
        return 80

    if matches == 1:
        return 60

    return 0


# =========================================================
# 🏆 WEIGHTED OVERALL SCORE
# =========================================================

def calculate_weighted_score(
    technical_score,
    project_score,
    experience_score,
    job_alignment_score,
    cloud_score,
    communication_score,
    education_score
):

    # Original requested weights:
    #
    # Technical Skills      20
    # Projects              20
    # Experience            15
    # Job Alignment         20
    # Cloud                  5
    # Communication         5
    # Education              5
    #
    # Total = 90
    #
    # We normalize by 90 so the final score
    # remains a proper 0-100 score.

    weighted_total = (

        technical_score * 20

        +

        project_score * 20

        +

        experience_score * 15

        +

        job_alignment_score * 20

        +

        cloud_score * 5

        +

        communication_score * 5

        +

        education_score * 5

    )

    overall_score = (
        weighted_total / 90
    )

    return int(
        max(
            0,
            min(overall_score, 100)
        )
    )


# =========================================================
# 🚀 ANALYZE RESUME
# =========================================================

@app.route(
    "/analyze",
    methods=["POST"]
)
def analyze():

    print("\n🔥 REQUEST RECEIVED")


    file = request.files.get(
        "resume"
    )

    job_desc = request.form.get(
        "jobDesc"
    ) or ""


    # -----------------------------------------------------
    # Check file
    # -----------------------------------------------------

    if not file:

        return jsonify({
            "error": "No file uploaded"
        }), 400


    # -----------------------------------------------------
    # Extract resume
    # -----------------------------------------------------

    resume_text = extract_text_from_pdf(
        file
    )

    resume_clean = clean(
        resume_text
    )

    job_clean = clean(
        job_desc
    )


    print(
        "📄 Resume Length:",
        len(resume_clean)
    )

    print(
        "📄 Job Description:",
        job_clean
    )


    # =====================================================
    # 🤖 WHOLE DOCUMENT AI SCORE
    # =====================================================

    if not job_clean.strip():

        ai_score = 0

    else:

        resume_embedding = model.encode(
            resume_clean,
            convert_to_tensor=True
        )

        job_embedding = model.encode(
            job_clean,
            convert_to_tensor=True
        )

        similarity = util.cos_sim(
            resume_embedding,
            job_embedding
        ).item()

        ai_score = int(
            max(
                0,
                min(
                    similarity * 100,
                    100
                )
            )
        )


    # =====================================================
    # 🔎 FIND JOB SKILLS
    # =====================================================

    resume_skills = extract_skills(
        resume_clean
    )

    job_skills = extract_skills(
        job_clean
    )


    # =====================================================
    # 🚨 ROLE FALLBACK
    # =====================================================

    if not job_skills:

        if "frontend" in job_clean:

            job_skills = [
                "html",
                "css",
                "javascript",
                "react"
            ]

        elif "backend" in job_clean:

            job_skills = [
                "node",
                "express",
                "mongodb",
                "sql"
            ]

        elif "machine learning" in job_clean:

            job_skills = [
                "python",
                "machine learning",
                "data science"
            ]

        elif "data analyst" in job_clean:

            job_skills = [
                "python",
                "sql",
                "data science"
            ]

        else:

            job_skills = [
                "python",
                "sql"
            ]


    # =====================================================
    # 🧠 EVIDENCE-BASED SKILL ANALYSIS
    # =====================================================

    skill_evidence = analyze_skill_evidence(
        resume_text,
        job_skills
    )


    # =====================================================
    # 🎯 TECHNICAL SCORE
    # =====================================================

    technical_score = calculate_technical_score(
        skill_evidence
    )


    # =====================================================
    # 🧠 SEMANTIC JOB REQUIREMENT MATCHING
    # =====================================================

    semantic_matches = semantic_job_matching(
        resume_text,
        job_desc
    )


    # =====================================================
    # 🎯 JOB ALIGNMENT SCORE
    # =====================================================

    if semantic_matches:

        semantic_scores = [
            item["score"]
            for item in semantic_matches
        ]

        job_alignment_score = int(
            sum(semantic_scores)
            /
            len(semantic_scores)
        )

    else:

        job_alignment_score = ai_score


    # =====================================================
    # 📁 PROJECT SCORE
    # =====================================================

    project_score = calculate_project_score(
        resume_clean
    )


    # =====================================================
    # 💼 EXPERIENCE SCORE
    # =====================================================

    experience_score = calculate_experience_score(
        resume_clean
    )


    # =====================================================
    # ☁️ CLOUD SCORE
    # =====================================================

    cloud_score = calculate_cloud_score(
        resume_clean,
        job_clean
    )


    # =====================================================
    # 🗣️ COMMUNICATION SCORE
    # =====================================================

    communication_score = (
        calculate_communication_score(
            resume_clean
        )
    )


    # =====================================================
    # 🎓 EDUCATION SCORE
    # =====================================================

    education_score = (
        calculate_education_score(
            resume_clean
        )
    )


    # =====================================================
    # 🏆 FINAL WEIGHTED SCORE
    # =====================================================

    final_score = calculate_weighted_score(

        technical_score,

        project_score,

        experience_score,

        job_alignment_score,

        cloud_score,

        communication_score,

        education_score

    )


    # =====================================================
    # 🔎 OLD MATCHED / MISSING FIELDS
    # =====================================================

    matched_skills = [

        skill

        for skill in resume_skills

        if skill in job_skills

    ]


    missing_skills = [

        skill

        for skill in job_skills

        if skill not in resume_skills

    ]


    # =====================================================
    # 💡 SUGGESTIONS
    # =====================================================

    suggestions = []


    # Add suggestions for skills that are
    # not strongly supported.

    for item in skill_evidence:

        if item["status"] == "NOT DETECTED":

            suggestions.append(
                f"Add clear evidence of {item['skill']} "
                "if you have this experience."
            )

        elif item["status"] == "PARTIAL MATCH":

            suggestions.append(
                f"Strengthen the resume evidence "
                f"for {item['skill']}."
            )


    if project_score < 60:

        suggestions.append(
            "Add stronger project descriptions."
        )


    if experience_score < 60:

        suggestions.append(
            "Add relevant internship or "
            "experience details."
        )


    if job_alignment_score < 60:

        suggestions.append(
            "Improve alignment between your "
            "resume and the job description."
        )


    if not suggestions:

        suggestions.append(
            "Great match 👍"
        )


    # =====================================================
    # 🧪 DEBUG OUTPUT
    # =====================================================

    print("\n====================================")
    print("🤖 WHOLE AI SCORE:", ai_score)
    print(
        "💻 TECHNICAL SCORE:",
        technical_score
    )
    print(
        "📁 PROJECT SCORE:",
        project_score
    )
    print(
        "💼 EXPERIENCE SCORE:",
        experience_score
    )
    print(
        "🎯 JOB ALIGNMENT:",
        job_alignment_score
    )
    print(
        "☁️ CLOUD SCORE:",
        cloud_score
    )
    print(
        "🗣️ COMMUNICATION SCORE:",
        communication_score
    )
    print(
        "🎓 EDUCATION SCORE:",
        education_score
    )
    print(
        "🏆 OVERALL SCORE:",
        final_score
    )
    print("====================================")


    print("\n====================================")
    print("🔎 EVIDENCE-BASED SKILL ANALYSIS")
    print("====================================")


    for item in skill_evidence:

        print(
            "\nSkill:",
            item["skill"]
        )

        print(
            "Status:",
            item["status"]
        )

        print(
            "Score:",
            item["score"]
        )

        print(
            "Evidence:",
            item["evidence"]
        )

        print(
            "Message:",
            item["message"]
        )


    print("\n====================================")


    # =====================================================
    # 📤 RETURN RESULTS
    # =====================================================

    return jsonify({

        # Existing fields
        "match_score": final_score,

        "ai_score": ai_score,

        "skill_score": technical_score,

        "matched_skills": matched_skills,

        "missing_skills": missing_skills,

        "suggestions": suggestions,


        # Semantic requirement analysis
        "semantic_score": job_alignment_score,

        "semantic_matches": semantic_matches,


        # Weighted scores
        "technical_score": technical_score,

        "project_score": project_score,

        "experience_score": experience_score,

        "job_alignment_score": job_alignment_score,

        "cloud_score": cloud_score,

        "communication_score": communication_score,

        "education_score": education_score,


        # NEW: evidence-based analysis
        "skill_evidence": skill_evidence

    })


# =========================================================
# ▶️ START SERVER
# =========================================================

if __name__ == "__main__":

    print(
        "🚀 Running on http://127.0.0.1:5001"
    )

    app.run(
        port=5001,
        debug=True
    )