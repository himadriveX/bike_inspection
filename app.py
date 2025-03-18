import streamlit as st
import time
from PIL import Image

# Configure the Streamlit page
st.set_page_config(
    page_title="Vehicle Inspection Dashboard",
    page_icon="🚗",
    layout="wide"
)

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'inspection_reports' not in st.session_state:
    st.session_state.inspection_reports = {}

# Hardcoded login credentials
USERNAME = "admin"
PASSWORD = "password123"

def login():
    st.title("Vehicle Inspection Dashboard")
    st.subheader("Login")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")

def main_dashboard():
    st.title("Vehicle Inspection Dashboard")
    
    # File upload section
    st.header("Upload Files for Inspection")
    uploaded_files = st.file_uploader(
        "Upload images or videos for inspection",
        type=["jpg", "jpeg", "png", "mp4", "avi", "mov"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        for file in uploaded_files:
            if file not in st.session_state.uploaded_files:
                st.session_state.uploaded_files.append(file)
                
                # Process file (simulated)
                with st.spinner(f'Processing {file.name}...'):
                    # Simulate processing time
                    time.sleep(2)
                    
                    # Generate mock inspection report
                    st.session_state.inspection_reports[file.name] = {
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'damages': [
                            'Minor scratch on front bumper',
                            'Paint chip on driver side door',
                            'Small dent on rear fender'
                        ],
                        'severity': 'Low',
                        'estimated_repair_cost': '$500-$800'
                    }
    
    # Display inspection reports
    if st.session_state.inspection_reports:
        st.header("Inspection Reports")
        for filename, report in st.session_state.inspection_reports.items():
            with st.expander(f"Report for {filename}"):
                st.write(f"**Inspection Time:** {report['timestamp']}")
                st.write("**Detected Damages:**")
                for damage in report['damages']:
                    st.write(f"- {damage}")
                st.write(f"**Severity Level:** {report['severity']}")
                st.write(f"**Estimated Repair Cost:** {report['estimated_repair_cost']}")
                
                # If the file is an image, display it
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    try:
                        image = Image.open(st.session_state.uploaded_files[
                            [f.name for f in st.session_state.uploaded_files].index(filename)
                        ])
                        st.image(image, caption=filename)
                    except Exception as e:
                        st.error(f"Error displaying image: {str(e)}")

    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.uploaded_files = []
        st.session_state.inspection_reports = {}
        st.rerun()

# Main app logic
if not st.session_state.logged_in:
    login()
else:
    main_dashboard()