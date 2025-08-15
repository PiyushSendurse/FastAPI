import streamlit as st
import requests

# Streamlit app title
st.title("Chatbot Login")

# Initialize session state for login status and user info
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.email = None

# If not logged in, show login form
if not st.session_state.logged_in:
    email = st.text_input("Email", placeholder="Enter your email")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    if st.button("Login"):
        # Call the FastAPI login endpoint
        try:
            resp = requests.post("http://localhost:8000/login", json={"email": email, "password": password})
        except Exception as e:
            st.error("Unable to connect to login service. Is FastAPI running?")
            st.stop()
        if resp.status_code == 200:
            data = resp.json()
            # Save login state and user info
            st.session_state.logged_in = True
            st.session_state.user_role = data.get("role", "")
            st.session_state.email = data.get("email", "")
            # Show a success message and proceed
            st.success(f"Logged in as **{st.session_state.user_role}**")
            st.rerun()  # reload the app to show the chatbot UI
        else:
            st.error("Invalid email or password. Please try again.")

# If logged in, show the chat interface
if st.session_state.logged_in:
    role = st.session_state.user_role  # "manager" or "employee"
    # Display a header or sidebar indicating the role
    if role.lower() == "manager":
        st.sidebar.success("Manager Mode")  # green highlight
    else:
        st.sidebar.info("Employee Mode")    # blue highlight

    st.header(f"Chatbot Interface ({role.capitalize()})")
    question = st.text_input("Ask a question:")
    if st.button("Submit Question"):
        if question.strip() == "":
            st.warning("Please enter a question.")
        else:
            # Call the FastAPI ask endpoint
            try:
                resp = requests.post("http://localhost:8000/ask", json={"question": question})
            except Exception as e:
                st.error("Unable to connect to Q&A service. Ensure FastAPI is running.")
                st.stop()
            if resp.status_code == 200:
                answer = resp.json().get("answer", "")
                st.write(f"**Answer:** {answer}")
            elif resp.status_code == 404:
                st.warning("Question not found in the database. Please try another question.")
            else:
                st.error(f"Error: {resp.status_code} - {resp.text}")
