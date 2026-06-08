import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="CodeMentor AI", page_icon="🧠", layout="wide")
st.title("🧠 CodeMentor AI")
st.subheader("Your Personalized Programming Tutor")

with st.sidebar:
    st.header("Student Setup")
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    if st.button("Register / Login"):
        response = requests.post(f"{API_URL}/student/students/register", json={"name": name, "email": email})
        if response.status_code == 200:
            data = response.json()
            st.session_state["student_id"] = data["student_id"]
            st.success(f"Welcome, {name}! ID: {data['student_id']}")
        elif response.status_code == 400:
            login = requests.get(f"{API_URL}/student/students/email/{email}")
            if login.status_code == 200:
                data = login.json()
                st.session_state["student_id"] = data["id"]
                st.success(f"Welcome back, {name}! ID: {data['id']}")
            else:
                st.error("Login failed. Check your email.")
        else:
            st.error(response.json().get("detail", "Error occurred"))

st.markdown("---")

if "student_id" not in st.session_state:
    st.info("Please register or login from the sidebar to start.")
else:
    st.markdown(f"**Logged in as Student ID:** {st.session_state['student_id']}")

    topic = st.text_input("Topic (e.g. loops, functions, recursion)", value="general")
    language = st.selectbox("Language", ["python", "javascript", "java", "c++"])
    code = st.text_area("Paste your code here", height=250)

    if st.button("Get Feedback 🚀"):
        if not code.strip():
            st.warning("Please paste some code first.")
        else:
            with st.spinner("CodeMentor is analyzing your code..."):
                response = requests.post(f"{API_URL}/tutor/tutor/analyze", json={
                    "student_id": st.session_state["student_id"],
                    "code": code,
                    "language": language,
                    "topic": topic
                })
            if response.status_code == 200:
                data = response.json()
                st.markdown("### 📝 Feedback")
                st.markdown(data["feedback"])
                st.caption(f"Session #{data['session']}")
            else:
                st.error("Something went wrong. Is the backend running?")