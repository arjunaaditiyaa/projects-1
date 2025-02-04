import os
import google.generativeai as genai
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms.base import LLM
from typing import List, Optional
from langchain.schema import Generation, LLMResult
import traceback
import streamlit as st
import pandas as pd
from collections import Counter
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Customer Feedback Analyzer", layout="wide")

st.markdown("""
<style>
    /* Global Styles */
    body {
        font-family: 'Roboto', sans-serif;
        background-color: #f5f7fa;
        color: #333;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #00FFFF;
        font-weight: 600;
    }
    h1 {
        font-size: 2.5rem;
        margin-bottom: 1.5rem;
    }
    h2 {
        font-size: 1.8rem;
        margin-bottom: 1rem;
    }
    h3 {
        font-size: 1.3rem;
        margin-bottom: 0.8rem;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        padding: 10px;
        font-size: 1rem;
        color: #333;
        transition: border-color 0.3s;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #3498db;
        box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #3498db;
        color: white;
        font-weight: 500;
        border-radius: 4px;
        padding: 10px 20px;
        border: none;
        transition: background-color 0.3s, transform 0.2s;
    }
    .stButton > button:hover {
        background-color: #2980b9;
        transform: translateY(-2px);
    }
    
    /* Metric Boxes */
    .metric-box {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: transform 0.3s;
    }
    .metric-box:hover {
        transform: translateY(-5px);
    }
    .metric-box h2 {
        color: #3498db;
        margin: 0 0 10px 0;
        font-size: 1.2rem;
    }
    .metric-box p {
        color: #2c3e50;
        margin: 0;
        font-size: 2rem;
        font-weight: 600;
    }
    
    .guidelines-box {
        background-color: #f8f9fa;
        border-left: 4px solid #3498db;
        padding: 20px 20px 20px 60px;
        border-radius: 4px;
        margin-top: 20px;
        position: relative;
    }
    .guidelines-box::before {
        content: "📋";
        font-size: 2rem;
        position: absolute;
        left: 20px;
        top: 50%;
        transform: translateY(-50%);
    }
    .guidelines-box h3 {
        color: #3498db;
        margin-top: 0;
        font-size: 1.2rem;
        margin-bottom: 10px;
    }
    .guidelines-box ul {
        padding-left: 20px;
        margin-bottom: 0;
        color: #555;
    }
    .guidelines-box li {
        margin-bottom: 8px;
    }
    
    /* Charts and Graphs */
    .plotly-graph-div {
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        padding: 15px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)
def configure_gemini_model(api_key: str):
    genai.configure(api_key=api_key)

def generate_gemini_text(prompt, model_name="gemini-1.5-pro"):
    try:
        model = genai.GenerativeModel(model_name=model_name)
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text
        else:
            return "Empty response received"
    except Exception as e:
        print("An error occurred while generating content:")
        traceback.print_exc()
        return str(e)

class GeminiLLM(LLM):
    model_name: str = "gemini-1.5-pro"
    max_new_tokens: int = 1000

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        return generate_gemini_text(prompt, self.model_name)

    def _generate(self, prompts: List[str], stop: Optional[List[str]] = None) -> LLMResult:
        generations = []
        for prompt in prompts:
            text = self._call(prompt, stop)
            generations.append([Generation(text=text)])
        return LLMResult(generations=generations)

    @property
    def _llm_type(self) -> str:
        return "gemini"

api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    configure_gemini_model(api_key)
else:
    raise ValueError("Google API key not found in environment variables.")

gemini_llm = GeminiLLM()

if 'feedback_df' not in st.session_state:
    st.session_state.feedback_df = pd.DataFrame(columns=['Timestamp', 'Feedback', 'Main Causes'])

if 'causes_counter' not in st.session_state:
    st.session_state.causes_counter = Counter()

if 'last_analysis_date' not in st.session_state:
    st.session_state.last_analysis_date = datetime.now()

individual_prompt_template = PromptTemplate(
    input_variables=["feedback"],
    template="""
    Analyze the following customer feedback and identify the main causes of dissatisfaction:

    {feedback}

    Provide only the main causes as single words or short phrases (2-3 words maximum).

    Format the response as follows:
    Main Causes:
    - [Cause 1]
    - [Cause 2]
    - [Cause 3]
    """
)

bulk_prompt_template = PromptTemplate(
    input_variables=["feedback_summary"],
    template="""
    Analyze the following summary of customer feedback:

    {feedback_summary}

    Provide a comprehensive analysis including:
    1. Top 10 recurring issues
    2. Suggested improvements for each issue
    3. Potential root causes for these issues

    Format your response as follows:
    
    Top 5 Recurring Issues:
    1. [Issue 1]
    2. [Issue 2]
    3. [Issue 3]
    4. [Issue 4]
    5. [Issue 5]
    6. [Issue 6]
    7. [Issue 7]
    8. [Issue 8]
    9. [Issue 9]
    10. [Issue 10]

    Suggested Improvements:
    1. [Issue 1]:
       - [Improvement 1]
       - [Improvement 2]
    2. [Issue 2]:
       - [Improvement 1]
       - [Improvement 2]
    ...

    Potential Root Causes:
    1. [Issue 1]: [Root cause explanation]
    2. [Issue 2]: [Root cause explanation]
    ...
    """
)

individual_llm_chain = LLMChain(llm=gemini_llm, prompt=individual_prompt_template)
bulk_llm_chain = LLMChain(llm=gemini_llm, prompt=bulk_prompt_template)

def analyze_individual_feedback(feedback: str) -> str:
    return individual_llm_chain.predict(feedback=feedback)

def extract_main_causes(analysis):
    causes = []
    if "Main Causes:" in analysis:
        causes_section = analysis.split("Main Causes:")[1]
        causes = [line.strip("- ").strip().lower() for line in causes_section.split("\n") if line.strip().startswith("-")]
    return causes

def analyze_bulk_feedback(feedback_summary: str) -> str:
    return bulk_llm_chain.predict(feedback_summary=feedback_summary)

st.sidebar.title("📊 Navigation")
page = st.sidebar.radio("Go to", ["🖊️ Submit Feedback", "📈 Dashboard"])

if page == "🖊️ Submit Feedback":
    st.header("Submit Your Feedback")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        feedback = st.text_area("Please share your thoughts:", height=200, placeholder="Type your feedback here...")

    with col2:
        st.markdown("""
<div class="guidelines-box">
    <h3>Guidelines for effective feedback:</h3>
    <ul>
        <li>Be specific and detailed</li>
        <li>Focus on both positive and negative aspects</li>
        <li>Provide constructive suggestions</li>
        <li>Use clear and concise language</li>
    </ul>
</div>
""", unsafe_allow_html=True)

    if st.button("📤 Submit Feedback", key="submit_feedback"):
        if feedback:
            with st.spinner("Analyzing your feedback..."):
                analysis = analyze_individual_feedback(feedback)
                main_causes = extract_main_causes(analysis)
                
                new_row = pd.DataFrame({
                    'Timestamp': [datetime.now()],
                    'Feedback': [feedback], 
                    'Main Causes': [main_causes]
                })
                st.session_state.feedback_df = pd.concat([st.session_state.feedback_df, new_row], ignore_index=True)
                
                st.session_state.causes_counter.update(main_causes)
            
            st.success("Thank you! Your feedback has been submitted and analyzed successfully.")
            st.balloons()
        else:
            st.warning("Please enter some feedback before submitting.")

elif page == "📈 Dashboard":
    st.header("Feedback Analysis Dashboard")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_feedback = len(st.session_state.feedback_df)
        st.markdown(f"""
        <div class="metric-box">
            <h2>Total Feedback</h2>
            <p>{total_feedback}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        unique_causes = len(st.session_state.causes_counter)
        st.markdown(f"""
        <div class="metric-box">
            <h2>Unique Causes</h2>
            <p>{unique_causes}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.session_state.causes_counter:
            top_cause = max(st.session_state.causes_counter, key=st.session_state.causes_counter.get)
            st.markdown(f"""
            <div class="metric-box">
                <h2>Top Cause</h2>
                <p>{top_cause}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-box">
                <h2>Top Cause</h2>
                <p>N/A</p>
            </div>
            """, unsafe_allow_html=True)

    st.subheader("Recent Feedback Analysis")

    if st.button("🔍 Analyze Recent Feedback", key="analyze_feedback"):
        current_date = datetime.now()
        start_date = datetime.min
        
        recent_feedback = st.session_state.feedback_df[st.session_state.feedback_df['Timestamp'] > start_date]
        
        if not recent_feedback.empty:
            feedback_summary = "\n".join(recent_feedback['Feedback'].tolist())
            bulk_analysis = analyze_bulk_feedback(feedback_summary)
            
            st.subheader("📊 Analysis Results")
            st.write(bulk_analysis)

            recurring_issues_df = pd.DataFrame(columns=['Issue', 'Improvements', 'Root Cause'])

            lines = bulk_analysis.split('\n')
            current_section = ""
            current_issue = ""
            improvements = []
            root_cause = ""
            
            for line in lines:
                if "Top 5 Recurring Issues:" in line:
                    current_section = "issues"
                elif "Suggested Improvements:" in line:
                    current_section = "improvements"
                elif "Potential Root Causes:" in line:
                    current_section = "root_causes"
                elif line.strip():
                    if current_section == "issues":
                        current_issue = line.split('. ', 1)[1] if '. ' in line else line
                    elif current_section == "improvements":
                        if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                            if improvements:
                                r={
                                    'Issue': current_issue,
                                    'Improvements': ', '.join(improvements),
                                    'Root Cause': ''
                                }
                                recurring_issues_df.loc[len(recurring_issues_df)] = r
                            current_issue = line.split(': ', 1)[1] if ': ' in line else line
                            improvements = []
                        elif line.strip().startswith('-'):
                            improvements.append(line.strip('- ').strip())
                    elif current_section == "root_causes":
                        if ': ' in line:
                            issue, cause = line.split(': ', 1)
                            idx = recurring_issues_df.index[recurring_issues_df['Issue'] == issue].tolist()
                            if idx:
                                recurring_issues_df.at[idx[0], 'Root Cause'] = cause
            
            if improvements:
                r={
                    'Issue': current_issue,
                    'Improvements': ', '.join(improvements),
                    'Root Cause': ''
                }
                recurring_issues_df.loc[len(recurring_issues_df)] = r
            
            st.subheader("🔄 Recurring Issues and Improvements")
            st.dataframe(recurring_issues_df, use_container_width=True)
            
            causes_df = pd.DataFrame.from_dict(st.session_state.causes_counter, orient='index', columns=['Count']).reset_index()
            causes_df.columns = ['Cause', 'Count']
            causes_df = causes_df.sort_values('Count', ascending=False).head(10)

            fig1 = px.bar(causes_df, x='Cause', y='Count', title='Top 10 Causes of Customer Dissatisfaction')
            st.plotly_chart(fig1, use_container_width=True)

            fig2 = px.pie(causes_df, values='Count', names='Cause', title='Distribution of Top Causes')
            st.plotly_chart(fig2, use_container_width=True)

            st.session_state.feedback_df['Date'] = pd.to_datetime(st.session_state.feedback_df['Timestamp']).dt.date
            feedback_timeline = st.session_state.feedback_df.groupby('Date').size().reset_index(name='Count')
            fig3 = px.line(feedback_timeline, x='Date', y='Count', title='Feedback Submission Timeline')
            st.plotly_chart(fig3, use_container_width=True)

            st.session_state.last_analysis_date = current_date
        else:
            st.warning("No feedback data available for analysis.")

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📋 View All Stored Feedback", key="view_feedback"):
            st.write(st.session_state.feedback_df)

    with col2:
        if st.button("🔢 View All Causes", key="view_causes"):
            st.write(dict(st.session_state.causes_counter))

    if st.button("🗑️ Reset Feedback Data", key="reset_data"):
        st.session_state.feedback_df = pd.DataFrame(columns=['Timestamp', 'Feedback', 'Main Causes'])
        st.session_state.causes_counter = Counter()
        st.session_state.last_analysis_date = datetime.now()
        st.success("Feedback data has been reset.")
        st.balloons()
