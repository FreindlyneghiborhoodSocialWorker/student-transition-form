import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from fpdf import FPDF
import datetime
import base64

# ---------------- GOOGLE SHEETS SETUP ----------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
SHEET_NAME = "Student Transition Data"

# Load credentials from Streamlit Secrets instead of a local file
service_account_info = st.secrets["gcp_service_account"]
credentials = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
client = gspread.authorize(credentials)


try:
    sheet = client.open(SHEET_NAME)
except Exception as e:
    st.error(f"Could not open Google Sheet: {e}")
    st.stop()

# ---------------- STREAMLIT APP ----------------
st.title("Student Transition Planning Form")

with st.form("student_form"):
    st.subheader("General Information")
    student_name = st.text_input("Student Name")
    student_email = st.text_input("Student Email")
    teacher_email = st.text_input("Teacher Email")
    school = st.text_input("School")
    grade = st.text_input("Grade")
    student_id = st.text_input("Student ID")
    date_completed = st.date_input("Date Completed", datetime.date.today())
    future_plans = st.text_input("Future Plans")
    absences = st.text_input("Absences (e.g., 8+ days)")
    attendance_concern = st.radio("Attendance Concern?", ["Yes", "No"])

    st.subheader("Graduation Progress & Exit Warnings")
    missing_credits = st.text_input("Missing Credits")
    state_test = st.text_input("State Test")
    exit_credential = st.text_input("Exit Credential")
    irc_points = st.text_input("IRC Points")
    test_eoc_scores = st.text_input("Test EOC Scores")
    met_test_requirement = st.text_input("Met Test Requirement")

    st.subheader("Work Preferences")
    work_with = st.multiselect("Work With", ["Others", "Alone"])
    work_position = st.multiselect("Work Position", ["Standing", "Sitting"])
    work_environment = st.multiselect("Work Environment", ["Inside", "Outside"])
    noise_pref = st.multiselect("Noise Preference", ["Quiet", "Noisy"])
    clean_pref = st.multiselect("Cleanliness Preference", ["Clean", "Dirty"])

    st.subheader("Career Interests")
    career_interests = st.text_area("Career Interests")

    st.subheader("PINS Needs")
    needs_score = st.slider("Local Needs Assessment Score (0-20)", 0, 20, 0)
    needs = st.text_area("Needs")
    strengths = st.text_area("Strengths")

    st.subheader("Teacher Input")
    teacher_interests = st.text_area("Teacher Identified Interests")
    teacher_needs = st.text_area("Teacher Identified Needs")

    st.subheader("Family Input")
    best_contact = st.text_input("Best Contact")
    family_concerns = st.text_area("Family Concerns")
    agency_requests = st.text_area("Agency Requests")
    iep_questions = st.text_area("IEP Team Questions/Concerns")
    family_goals = st.text_area("Family Goals Post High School")
    form_completed_by = st.text_input("Form Completed By")

    st.subheader("Non-School Agencies")
    ood_name = st.text_input("OOD Counselor Name")
    ood_email = st.text_input("OOD Contact Email")
    ood_phone = st.text_input("OOD Phone")
    dds_name = st.text_input("DDS Counselor Name")
    dds_email = st.text_input("DDS Contact Email")
    dds_phone = st.text_input("DDS Phone")

    st.subheader("Areas Where Family Requests Help")
    col10, col11, col12, col13 = st.columns(4)
    with col10:
        help_transport = st.checkbox("Transportation")
    with col11:
        help_health = st.checkbox("Health")
    with col12:
        help_self_advocacy = st.checkbox("Self-advocacy")
    with col13:
        help_training = st.checkbox("Training")

    job_help = st.text_input("Job-related Help")

    # ✅ Submit button inside form
    submitted = st.form_submit_button("Submit & Generate PDF", use_container_width=True)

# ---------------- PDF GENERATION ----------------
if submitted:
    pdf = FPDF()
    pdf.add_page()

    # ✅ Add Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 12, "Student Transition Planning Summary", ln=True, align="C")
    pdf.ln(10)

    def add_colored_section(title, content_list, bg_color, highlight_rules=None):
        pdf.set_fill_color(*bg_color)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 8, title, ln=True, fill=True)

        pdf.set_font("Arial", size=12)
        for item in content_list:
            if not item:
                continue

            pdf.set_text_color(0, 0, 0)
            style = ""

            if highlight_rules:
                for rule in highlight_rules:
                    if rule["match"].lower() in item.lower():
                        pdf.set_text_color(*rule.get("color", (0, 0, 0)))
                        style = rule.get("style", "")
                        break

            if style == "B":
                pdf.set_font("Arial", "B", 12)
            elif style == "I":
                pdf.set_font("Arial", "I", 12)
            else:
                pdf.set_font("Arial", size=12)

            pdf.multi_cell(0, 8, f"- {item}")
            pdf.set_font("Arial", size=12)
            pdf.set_text_color(0, 0, 0)

        pdf.ln(2)

    # --- Build each section ---
    add_colored_section("General Information", [
        f"Student Name: {student_name}",
        f"Student Email: {student_email}",
        f"Teacher Email: {teacher_email}",
        f"School: {school}",
        f"Grade: {grade}",
        f"Student ID: {student_id}",
        f"Date Completed: {date_completed}",
        f"Future Plans: {future_plans}",
        f"Absences: {absences}",
        f"Attendance Concern: {attendance_concern}"
    ], bg_color=(173, 216, 230),
    highlight_rules=[
        {"match": "Student Name", "style": "B", "color": (0, 0, 139)},
        {"match": "Student Email", "style": "B", "color": (0, 0, 139)}
    ])

    add_colored_section("Graduation Progress & Exit Warnings", [
        f"Missing Credits: {missing_credits}",
        f"State Test: {state_test}",
        f"Exit Credential: {exit_credential}",
        f"IRC Points: {irc_points}",
        f"Test EOC Scores: {test_eoc_scores}",
        f"Met Test Requirement: {met_test_requirement}"
    ], bg_color=(255, 255, 153),
    highlight_rules=[
        {"match": "In Progress", "color": (255, 0, 0), "style": "B"}
    ])

    add_colored_section("Work Preferences", [
        f"Work With: {', '.join(work_with)}",
        f"Work Position: {', '.join(work_position)}",
        f"Work Environment: {', '.join(work_environment)}",
        f"Noise Preference: {', '.join(noise_pref)}",
        f"Cleanliness Preference: {', '.join(clean_pref)}"
    ], bg_color=(144, 238, 144),
    highlight_rules=[
        {"match": "Work With: Others", "style": "B", "color": (0,100,0)},
        {"match": "Work Environment: Inside", "style": "B", "color": (0,100,0)}
    ])

    add_colored_section("Career Interests", [career_interests],
        bg_color=(216, 191, 216),
        highlight_rules=[{"match": "uplift people and empower", "style": "I", "color": (128, 0, 128)}]
    )

    add_colored_section("PINS Needs", [
        f"Needs Score: {needs_score}",
        f"Needs: {needs}",
        f"Strengths: {strengths}"
    ], bg_color=(255, 228, 181),
    highlight_rules=[
        {"match": f"Needs Score: {needs_score}", "style": "B", "color": (255,140,0)}
    ])

    add_colored_section("Teacher Input", [
        f"Interests: {teacher_interests}",
        f"Needs: {teacher_needs}"
    ], bg_color=(211, 211, 211),
    highlight_rules=[
        {"match": "long walks on the beach and getting ice cream", "style": "I", "color": (105,105,105)}
    ])

    add_colored_section("Family Input", [
        f"Best Contact: {best_contact}",
        f"Family Concerns: {family_concerns}",
        f"Agency Requests: {agency_requests}",
        f"IEP Questions: {iep_questions}",
        f"Family Goals: {family_goals}",
        f"Form Completed By: {form_completed_by}"
    ], bg_color=(255, 182, 193),
    highlight_rules=[
        {"match": "Family Goals", "style": "B", "color": (255,20,147)}
    ])

    add_colored_section("Non-School Agencies", [
        f"OOD Counselor: {ood_name} ({ood_email}, {ood_phone})",
        f"DDS Counselor: {dds_name} ({dds_email}, {dds_phone})"
    ], bg_color=(175, 238, 238),
    highlight_rules=[
        {"match": "Counselor", "style": "B", "color": (0,128,128)}
    ])

    add_colored_section("Areas Where Family Requests Help", [
        "Transportation" if help_transport else "",
        "Health" if help_health else "",
        "Self-advocacy" if help_self_advocacy else "",
        "Training" if help_training else "",
        f"Job Help: {job_help}"
    ], bg_color=(255, 204, 203),
    highlight_rules=[
        {"match": "Transportation", "style": "B", "color": (178,34,34)},
        {"match": "Self-advocacy", "style": "B", "color": (178,34,34)}
    ])

    # Save PDF
    filename = f"{student_name}_{date_completed}.pdf".replace(" ", "_")
    pdf.output(filename)

    # Show download button
    with open(filename, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode("utf-8")
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">📥 Download {filename}</a>'
        st.markdown(href, unsafe_allow_html=True)

    # ---------------- SAVE TO GOOGLE SHEETS ----------------
    county = "Ashland" if "ashland" in school.lower() else "Wayne"
    try:
        worksheet = sheet.worksheet(county)
    except:
        worksheet = sheet.add_worksheet(title=county, rows="100", cols="20")

    worksheet.append_row([
        str(datetime.date.today()), student_name, student_email, teacher_email,
        school, grade, student_id, str(date_completed), future_plans,
        absences, attendance_concern, missing_credits, state_test, exit_credential,
        irc_points, test_eoc_scores, met_test_requirement, ", ".join(work_with),
        ", ".join(work_position), ", ".join(work_environment), ", ".join(noise_pref),
        ", ".join(clean_pref), career_interests, needs_score, needs, strengths,
        teacher_interests, teacher_needs, best_contact, family_concerns,
        agency_requests, iep_questions, family_goals, form_completed_by,
        ood_name, ood_email, ood_phone, dds_name, dds_email, dds_phone,
        "Transportation" if help_transport else "",
        "Health" if help_health else "",
        "Self-advocacy" if help_self_advocacy else "",
        "Training" if help_training else "",
        job_help
    ])

    st.success("✅ Form submitted successfully!")
