import streamlit as st
from resume_reader import extract_text_from_pdf
from skill_matcher import load_skills, match_skills
from skill_resources import skill_resources
from io import BytesIO
from fpdf import FPDF
import base64
import requests

# Page config
st.set_page_config(page_title="SkillVault", page_icon="📂", layout="wide")

# Load animation (optional)
@st.cache_data
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Styling
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Segoe UI', sans-serif;
            background-color: #f8f9fa;
            color: #111;
        }
        .title-text {
            text-align: center;
            color: #1a237e;
            font-size: 36px;
            font-weight: bold;
            margin: 20px 0;
        }
        .section {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 1.5rem;
            margin-top: 1.5rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }
        .skill-card {
            padding: 10px;
            background-color: #e3f2fd;
            border-left: 5px solid #1976d2;
            border-radius: 6px;
            margin-bottom: 8px;
        }
        .missing-skill {
            background-color: #ffebee;
            border-left: 5px solid #d32f2f;
        }
        .metric-card {
            background-color: #fff3e0;
            padding: 15px;
            border-radius: 8px;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
            font-size: 18px;
            color: #000;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title-text'>SkillVault: Resume & Skill Analyzer</div>", unsafe_allow_html=True)

# Tabs instead of scrolling
tab1, tab2, tab3, tab4 = st.tabs(["Upload Resume", "Skill Match", "Suggestions", "Download Report"])

# Shared state
resume_text = ""
found_skills = []
missing_skills = []
match_score = 0
job_role = ""

with tab1:
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])
    job_role = st.selectbox("Select Job Role", ["data_analyst", "software_engineer", "database_developer", "machine_learning_engineer", "cloud_engineer"])
    if uploaded_file:
        resume_text = extract_text_from_pdf(uploaded_file)
        required_skills = load_skills(job_role)
        found_skills, missing_skills = match_skills(resume_text, required_skills)
        total_skills = len(found_skills) + len(missing_skills)
        match_score = round((len(found_skills) / total_skills) * 100) if total_skills > 0 else 0
        st.success("Resume successfully processed.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("Skill Match Score")
    if uploaded_file:
        st.markdown(f"<div class='metric-card'>Your Match Score: {match_score}%</div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Skills Found")
            for skill in found_skills:
                st.markdown(f"<div class='skill-card'>{skill}</div>", unsafe_allow_html=True)
        with col2:
            st.subheader("Missing Skills")
            for skill in missing_skills:
                st.markdown(f"<div class='skill-card missing-skill'>{skill}</div>", unsafe_allow_html=True)
    else:
        st.info("Please upload a resume in the Upload tab first.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("Learning Suggestions")
    if missing_skills:
        for skill in missing_skills:
            if skill in skill_resources:
                info = skill_resources[skill]
                st.markdown(f"""
                    <div class='skill-card missing-skill'>
                        <strong>{skill.title()}</strong><br>
                        {info['desc']}<br>
                        <a href="{info['link']}" target="_blank">Learn {skill}</a>
                    </div>
                """, unsafe_allow_html=True)
    elif uploaded_file:
        st.success("No missing skills. Great job!")
    else:
        st.info("Please upload your resume and go to 'Skill Match' tab first.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab4:
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("Download PDF Report")
    if uploaded_file:
        def generate_pdf():
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=14)
            pdf.cell(200, 10, txt="SkillVault Report", ln=1, align="C")
            pdf.ln(10)
            pdf.cell(200, 10, txt=f"Job Role: {job_role}", ln=1)
            pdf.cell(200, 10, txt=f"Skill Match Score: {match_score}%", ln=1)
            pdf.ln(5)

            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt="Skills Found:", ln=1)
            pdf.set_font("Arial", '', 12)
            for skill in found_skills:
                pdf.cell(200, 8, txt=f"- {skill}", ln=1)

            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt="Missing Skills:", ln=1)
            pdf.set_font("Arial", '', 12)
            for skill in missing_skills:
                pdf.cell(200, 8, txt=f"- {skill}", ln=1)

            buffer = BytesIO()
            pdf.output(buffer)
            buffer.seek(0)
            return buffer

        pdf_file = generate_pdf()
        b64 = base64.b64encode(pdf_file.read()).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="skillvault_report.pdf">Download SkillVault Report (PDF)</a>'
        st.markdown(href, unsafe_allow_html=True)
    else:
        st.info("No report available. Upload your resume first.")
    st.markdown("</div>", unsafe_allow_html=True)
