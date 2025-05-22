import streamlit as st
import requests

# Session state keys
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
    if "password" not in st.session_state:
        st.session_state.password = None
if "history" not in st.session_state:
    st.session_state.history = []

# API endpoints (replace with actual URLs)
API_BASE = " http://127.0.0.1:3800"
LOGIN_ENDPOINT = f"{API_BASE}/login"
SIGNUP_ENDPOINT = f"{API_BASE}/signup"
RESPONSE_ENDPOINT = f"{API_BASE}/generate"
HISTORY_ENDPOINT = f"{API_BASE}/history"

def login_view():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        response = requests.post(LOGIN_ENDPOINT, json={"username": username, "password": password})
        st.write(response.status_code)
        if response.status_code == 200:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.password = password
            st.success("Login successful")
        else:
            st.error("Invalid credentials")

    if st.button("Don't have an account? Sign up"):
        st.session_state["page"] = "signup"

def signup_view():
    st.title("Sign Up")
    username = st.text_input("New Username")
    password = st.text_input("Password", type="password")
    repassword = st.text_input("Re-enter Password", type="password")
    if st.button("Create Account"):
        if password != repassword:
            st.error("Passwords do not match.")
        else:
            response = requests.post(SIGNUP_ENDPOINT, json={"username": username, "password": password})
            if response.status_code == 200:
                st.success("Account created. Please login.")
                st.session_state["page"] = "login"
            else:
                st.error("Signup failed")

    if st.button("Already have an account? Login"):
        st.session_state["page"] = "login"

def main_ui():
    st.title("AI Query Interface")

    with st.sidebar:
        st.header("History")
        history_response = requests.get(f"{HISTORY_ENDPOINT}/{st.session_state.username}",json={"username": st.session_state.username, "password": st.session_state.password})
        if history_response.status_code == 200:
            history = history_response.json().get("history", [])
            for i, item in enumerate(reversed(history)):
                with st.expander(f"{item['query'][:min(len(item['query']), 60)]}"):
                    st.markdown(f"**Input:** {item['query']}")
                    st.markdown(f"**Response 1:** {item['casual_response']}")
                    st.markdown(f"**Response 2:** {item['formal_response']}")


    user_input = st.text_area("Enter your query")
    if st.button("Generate"):
        with st.spinner("Getting response..."):
            payload = {
                "user_id": st.session_state.username,
                "password": st.session_state.password,
                "query": user_input,
            }
            response = requests.post(RESPONSE_ENDPOINT, json=payload)
            if response.status_code == 200:
                data = response.json()
                casual = data.get("casual_response", "N/A")
                formal = data.get("formal_response", "N/A")

                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Formal Response")
                    st.write(formal)

                with col2:
                    st.subheader("Casual Response")
                    st.write(casual)


            else:
                st.error("Failed to get response.")


# Page logic
if "page" not in st.session_state:
    st.session_state.page = "login"

if not st.session_state.logged_in:
    if st.session_state.page == "login":
        login_view()
    elif st.session_state.page == "signup":
        signup_view()
else:
    main_ui()
