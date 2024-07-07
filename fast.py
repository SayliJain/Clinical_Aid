import streamlit as st
import openai
import asyncio
import aiohttp

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to generate response from OpenAI
async def generate_response(session, prompt):
    try:
        async with session.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {openai.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "You are an AI medical consultant for medical professionals with extensive knowledge and expertise in clinical medicine. Your role is to provide detailed and accurate analysis, diagnosis, and management recommendations for complex patient cases."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1500,
                "temperature": 0.7
            },
            ssl=False  # Disable SSL verification
        ) as response:
            result = await response.json()
            return result['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit UI
st.title("Patient History and Clinical Analysis")

# Instructions and Input Form
col1, col2 = st.columns(2)

with col1:
    st.header("Instructions")
    st.write("Please enter the patient history in the following format:")
    st.markdown("""
    - **Chief Concern**
    - **HPI (History of Present Illness)**
    - **ROS (Review of Systems)**
    - **PMHx (Past Medical History)**
    - **PSurgHx (Past Surgical History)**
    - **FHx (Family History)**
    - **SocHx (Social History)**
    - **HRB (Health Risk Behaviors)**
    - **Meds (Medications)**
    - **Allergies**
    - **Exam** 
    - **Lab Results**
    """)

with col2:
    st.header("Patient History Input")
    patient_history = st.text_area(
        "Enter/Paste your content here. Press Enter twice to save it.",
        height=400,
        placeholder="Enter patient history here..."
    )

if st.button("Generate Clinical Analysis"):
    if patient_history:
        # Define prompts for each section
        prompts = {
            "clinical_problem_representation": f"""
            Clinical Problem Representation:
            {patient_history}
            Provide a concise summary of the key clinical issues, findings, and diagnostic challenges presented in the case. Ensure the response integrates the patient's history, symptoms, physical examination, and test results.
            """,
            "most_likely_diagnosis": f"""
            Most Likely Diagnosis:
            {patient_history}
            Provide your primary most likely diagnostic hypothesis, supported by a detailed explanation that integrates the patient's history, symptoms, physical examination, and test results. Include any relevant pathophysiological mechanisms, epidemiological factors, or diagnostic criteria that support your diagnosis.
            """,
            "expanded_differential_diagnosis": f"""
            Expanded Differential Diagnosis:
            {patient_history}
            Provide a comprehensive list of differential diagnoses that should be considered, along with brief explanations for their inclusion in the differential. Evaluate the relative likelihood of each differential diagnosis based on the available information.
            """,
            "alternative_diagnosis": f"""
            Alternative Diagnosis:
            {patient_history}
            Provide a comprehensive list of alternative diagnoses that should be considered, along with brief explanations for their inclusion in alternative. Evaluate the relative likelihood of each alternative diagnosis based on the available information.
            """,
            "clinical_assessment": f"""
            Clinical Assessment:
            {patient_history}
            List specific diagnostic tests, procedures, or imaging studies that you recommend to confirm or rule out the suspected diagnosis, as well as any additional tests needed to evaluate the differential diagnoses or address any remaining diagnostic uncertainties.
            """,
            "clinical_treatment_plan": f"""
            Clinical Treatment Plan:
            {patient_history}
            You are a highly experienced clinician. Based on the detailed patient case provided below, create an elaborate clinical treatment plan that addresses the patient's condition comprehensively. Your response should include the most likely diagnosis, a thorough analysis of the patient's symptoms, a step-by-step treatment plan, and any necessary follow-up actions. Ensure the response is detailed and at least 400 words.
            """,
            "monitoring_and_follow_up": f"""
            Monitoring and Follow-Up:
            {patient_history}
            Provide comprehensive guidelines for monitoring the patient's response to treatment, potential complications or adverse effects to watch for, and recommended follow-up plans, including any necessary specialist referrals or additional testing.
            """
        }

        async def main():
            async with aiohttp.ClientSession() as session:
                tasks = [generate_response(session, prompt) for prompt in prompts.values()]
                responses = await asyncio.gather(*tasks)
                return dict(zip(prompts.keys(), responses))

        with st.spinner("Generating clinical analysis..."):
            responses = asyncio.run(main())

        # Display the final output with updated patient history in tabs
        st.header("Clinical Analysis Results")
        tabs = st.tabs([
            "Clinical Problem Representation", 
            "Most Likely Diagnosis", 
            "Expanded Differential Diagnosis", 
            "Alternative Diagnosis", 
            "Clinical Assessment", 
            "Clinical Treatment Plan", 
            "Monitoring and Follow-Up"
        ])

        with tabs[0]:
            st.subheader("Clinical Problem Representation")
            st.write(responses['clinical_problem_representation'])

        with tabs[1]:
            st.subheader("Most Likely Diagnosis")
            st.write(responses['most_likely_diagnosis'])

        with tabs[2]:
            st.subheader("Expanded Differential Diagnosis")
            st.write(responses['expanded_differential_diagnosis'])

        with tabs[3]:
            st.subheader("Alternative Diagnosis")
            st.write(responses['alternative_diagnosis'])

        with tabs[4]:
            st.subheader("Clinical Assessment")
            st.write(responses['clinical_assessment'])

        with tabs[5]:
            st.subheader("Clinical Treatment Plan")
            st.write(responses['clinical_treatment_plan'])

        with tabs[6]:
            st.subheader("Monitoring and Follow-Up")
            st.write(responses['monitoring_and_follow_up'])
    else:
        st.error("Please enter the patient history.")
