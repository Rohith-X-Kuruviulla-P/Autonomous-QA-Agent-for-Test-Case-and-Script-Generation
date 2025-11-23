import streamlit as st
import requests
import pandas as pd
import json

# UI Config
st.set_page_config(page_title="Sentinel-QA", layout="wide")
API_URL = "http://localhost:8000"

st.title("Sentinel-QA: Autonomous Testing Agent")
st.markdown("---")

# --- Sidebar: Phase 1 - Ingestion ---
with st.sidebar:
    st.header("1. Knowledge Base")
    uploaded_files = st.file_uploader(
        "Upload HTML & Docs (MD, TXT, PDF)", 
        accept_multiple_files=True
    )
    
    if st.button("Build Knowledge Base"):
        if uploaded_files:
            with st.spinner("Parsing & Embedding Documents..."):
                files = [("files", (f.name, f, f.type)) for f in uploaded_files]
                response = requests.post(f"{API_URL}/upload", files=files)
                
                if response.status_code == 200:
                    st.success(f"Success! {response.json()['chunks']} chunks stored.")
                else:
                    st.error("Ingestion Failed.")
        else:
            st.warning("Please upload files first.")

# --- Main Area: Phase 2 - Test Strategy ---
st.header("2. Test Strategy Agent")
user_query = st.text_input("Describe required tests (e.g., 'Generate positive tests for the checkout form')")

if st.button("Generate Test Cases"):
    with st.spinner("Agent is analyzing docs..."):
        response = requests.post(f"{API_URL}/generate-tests", data={"query": user_query})
        
        if response.status_code == 200:
            data = response.json()
            st.session_state['test_plan'] = data['test_cases']
        else:
            st.error(f"Error: {response.text}")

# Display Test Cases
if 'test_plan' in st.session_state:
    df = pd.DataFrame(st.session_state['test_plan'])
    st.dataframe(df, use_container_width=True)
    
    # --- Phase 3: Script Generation ---
    st.header("3. Automation Agent")
    
    # Find the HTML file in the uploaded list (logic assumption for UI)
    html_files = [f.name for f in uploaded_files if f.name.endswith(".html")] if uploaded_files else []
    selected_html = st.selectbox("Select Target HTML", html_files)
    
    # Select a specific test case
    selected_test_id = st.selectbox("Select Test Case to Automate", df['test_id'].tolist())
    
    if st.button("Generate Selenium Script"):
        if selected_html:
            # Find full test object
            test_case_obj = df[df['test_id'] == selected_test_id].to_dict(orient='records')[0]
            
            with st.spinner("Writing Python Code..."):
                payload = {
                    "test_case": json.dumps(test_case_obj),
                    "html_filename": selected_html
                }
                resp = requests.post(f"{API_URL}/generate-script", data=payload)
                
                if resp.status_code == 200:
                    code = resp.json().get("script", "# No code generated")
                    st.subheader("Generated Python Script")
                    st.code(code, language='python')
                else:
                    st.error("Script generation failed.")
        else:
            st.warning("Ensure an HTML file was uploaded and selected.")