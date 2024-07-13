import os
import google.generativeai as genai
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.llms.base import LLM
from pydantic import Field
from typing import List, Optional
from langchain.schema import Generation, LLMResult
import traceback
import streamlit as st
from gtts import gTTS
import tempfile

st.set_page_config(layout="wide")

video_html = """
    <style>
    #myVideo {
        position: fixed;
        right: 0;
        bottom: 0;
        min-width: 100%; 
        min-height: 100%;
    }
    .content {
        position: fixed;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        color: #f1f1f1;
        width: 100%;
        padding: 20px;
    }
    </style>    
    <video autoplay muted loop id="myVideo">
        <source src="https://static.streamlit.io/examples/star.mp4")>
    </video>
"""

st.markdown(video_html, unsafe_allow_html=True)

def configure_gemini_model(api_key: str):
    genai.configure(api_key=api_key)

def generate_gemini_text(prompt, model_name="gemini-1.5-flash"):
    try:
        model = genai.GenerativeModel(model_name=model_name)
        response = model.generate_content(prompt)
        if response and response.candidates:
            return response.candidates[0].content.parts[0].text
        else:
            return "Empty response received"
    except Exception as e:
        print("An error occurred while generating content:")
        traceback.print_exc()
        return str(e)

class GeminiLLM(LLM):
    model_name: str = "gemini-1.5-flash"
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

prompt_template = PromptTemplate(
    input_variables=["history", "input", "type", "genre"],
    template="You are an AI that helps generate {type} stories in the {genre} genre. Based on the following prompt and history, generate a continuation for the story:\n\nHistory: {history}\n\nPrompt: {input}\n\nContinuation:"
)
memory = ConversationBufferMemory(input_key="input", memory_key="history")
llm_chain = LLMChain(llm=gemini_llm, prompt=prompt_template, memory=memory)

def generate_story(story_type: str, genre: str, prompt: str) -> str:
    inputs = {
        "input": prompt,
        "type": story_type,
        "genre": genre
    }
    response = llm_chain.predict(**inputs)
    return response

st.header(":violet[Story Generator with Gemini]")
a = st.select_slider(":red[Enter the story type: ]", ('overcoming the monster', 'rags to riches', 'the quest', 'voyage/journey and return', 'rebirth', 'tragedy', 'comedy'))
b = st.select_slider(":red[Enter the story genre: ]", ('fantasy', 'historical', 'fiction', 'horror', 'mystery', 'romance', 'science fiction', 'relationship fiction', 'suspense', 'thrillers', 'action adventure'))
c = st.text_input(":red[Enter a story prompt: ]")
language=st.select_slider(":red[select the languages for the audio]",("en","fr","ar","cs","da","nl","fi","de","el","hi","hu","id","it","ja","ko","la","lv","pt","ro","ru","sr","sk","es","sv","ta","th","tr","vi","cy"))

if st.button("GENERATE"):
    story_continuation = generate_story(a, b, c)
    st.write(f":red[Story Continuation:\n{story_continuation}]\n")
    tts = gTTS(text=story_continuation, lang=language)
    with tempfile.NamedTemporaryFile(delete=False) as fp:
        tts.save(fp.name)
        st.audio(fp.name)
