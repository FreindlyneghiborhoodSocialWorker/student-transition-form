import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from fpdf import FPDF
import base64
import datetime

# -----------------------------
# 1. Page title
# -----------------------------
st.title("📘 Student Transition Planning Summary")

# -----------------------------
# 2. Google Sheets connection using Streamlit Secrets
# -----------------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# ✅ FIXED: use secrets, not file
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=SCOPES
)

# Authorize gspread client
client = gspread.authorize(creds)

# Replace with your sheet name
SHEET_NAME = "Student Transition Responses"
spreadsheet = client.open(SHEET_NAME)
worksheet = spreadsheet.sheet1

# -----------------------------
# 3. Streamlit form
# -----------------------------
with st.form("transition_form"):
    st.subheader("General Information")
    student_name = st.text_input("Student Name")
    student_email = st.text_input("Student Email")
    teacher_email = st.text_input("Teacher Email")
    school = st.text_input("School")
    grade = st.text_input("Grade")
    student_id = st.text_input("Student ID")
    date_completed = st.date_input("Date Completed", value=datetime.date.today())
    future_plans = st.text_area("Future Plans")

    st.subheader("Graduation Progress & Exit Warnings")
    missing_credits = st.text_input("Missing Credits")
    state_test = st.text_input("State Test")
    exit_credential = st.text_input("Exit Credential")
    irc_points = st.text_input("IRC Points")
    test_eoc_scores = st.radio("Test EOC Scores", ["Met Test Requirement", "In Progress"])

    st.subheader("Work Preferences")
    work_with = st.radio("Work With", ["Others", "Alone"])
    work_position = st.radio("Work Position", ["Standing", "Sitting"])
    work_environment = st.radio("Work Environment", ["Inside", "Outside"])
    noise_pref = st.radio("Noise Preference", ["Quiet", "Noisy"])
    cleanliness_pref = st.radio("Cleanliness Preference", ["Clean", "Dirty"])

    st.subheader("Career Interests")
    career_interests = st.text_area("Career Interests")

    st.subheader("PINS Needs")
    local_score = st.slider("Local Needs Assessment Score (0-20)", 0, 20, 10)
    needs = st.text_area("Needs")
    strengths = st.text_area("Strengths")

    st.subheader("Teacher Input")
    teacher_interests = st.text_area("Teacher Identified Interests")
    teacher_needs = st.text_area("Teacher Identified Needs")

    st.subheader("Family Input")
    family_contact = st.text_input("Best Contact")
    family_concerns = st.text_area("Family Concerns")
    agency_requests = st.text_area("Agency Requests")
    iep_questions = st.text_area("IEP Team Questions/Concerns")
    family_goals = st.text_area("Family Goals Post High School")

    st.subheader("Non-School Agencies")
    ood_counselor = st.text_input("OOD Counselor Name")
    ood_email = st.text_input("OOD Contact Email")
    ood_phone = st.text_input("OOD Phone")
    dds_counselor = st.text_input("DDS Counselor Name")
    dds_email = st.text_input("DDS Contact Email")
    dds_phone = st.text_input("DDS Phone")

    st.subheader("Areas Where Family Requests Help")
    help_transport = st.checkbox("Transportation")
    help_training = st.checkbox("Training")
    help_selfadvocacy = st.checkbox("Self-advocacy")
    help_job = st.checkbox("Getting a part-time job")

    submitted = st.form_submit_button("Submit Form")

# -----------------------------
# 4. Handle submission
# -----------------------------
if submitted:
    row = [
        student_name, student_email, teacher_email, school, grade, student_id, str(date_completed),
        future_plans, missing_credits, state_test, exit_credential, irc_points, test_eoc_scores,
        work_with, work_position, work_environment, noise_pref, cleanliness_pref,
        career_interests, local_score, needs, strengths,
        teacher_interests, teacher_needs,
        family_contact, family_concerns, agency_requests, iep_questions, family_goals,
        ood_counselor, ood_email, ood_phone,
        dds_counselor, dds_email, dds_phone,
        "Transportation" if help_transport else "",
        "Training" if help_training else "",
        "Self-advocacy" if help_selfadvocacy else "",
        "Part-time Job" if help_job else ""
    ]

    worksheet.append_row(row)

    # -----------------------------
    # 5. Generate PDF summary
    # -----------------------------
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Student Transition Planning Summary", ln=True, align="C")
    pdf.set_font("Arial", "", 12)

    def section(title, content, highlight=False):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, title, ln=True)
        pdf.set_font("Arial", "", 12)
        if highlight:
            pdf.set_text_color(220, 50, 50)  # red highlight
        pdf.multi_cell(0, 8, content)
        pdf.set_text_color(0, 0, 0)

    section("General Information", f"Name: {student_name}\nEmail: {student_email}\nSchool: {school}\nGrade: {grade}")
    section("Future Plans", future_plans)
    section("Graduation Progress", f"Missing Credits: {missing_credits}\nTest EOC: {test_eoc_scores}", highlight=(test_eoc_scores=="In Progress"))
    section("Work Preferences", f"With: {work_with}\nPosition: {work_position}\nEnvironment: {work_environment}\nNoise: {noise_pref}\nCleanliness: {cleanliness_pref}")
    section("Career Interests", career_interests)
    section("PINS Needs", f"Score: {local_score}\nNeeds: {needs}\nStrengths: {strengths}")
    section("Teacher Input", f"Interests: {teacher_interests}\nNeeds: {teacher_needs}")
    section("Family Input", f"Contact: {family_contact}\nConcerns: {family_concerns}\nGoals: {family_goals}")
    section("Agencies", f"OOD Counselor: {ood_counselor}, {ood_email}, {ood_phone}\nDDS Counselor: {dds_counselor}, {dds_email}, {dds_phone}")
    section("Family Help Areas", ", ".join([h for h in ["Transportation" if help_transport else "", "Training" if help_training else "", "Self-advocacy" if help_selfadvocacy else "", "Part-time Job" if help_job else ""] if h]))

    pdf_output = "student_summary.pdf"
    pdf.output(pdf_output)

    with open(pdf_output, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
        href = f'<a href="data:application/pdf;base64,{b64}" download="student_summary.pdf">📥 Download PDF</a>'
        st.markdown(href, unsafe_allow_html=True)

    st.success("✅ Form submitted! Data saved to Google Sheets and PDF generated.")
