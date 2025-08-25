SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=SCOPES
)


    st.success("✅ Form submitted successfully!")

