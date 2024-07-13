Story Generator with Gemini

Project Overview:
This project is a web application that generates stories based on user inputs, utilizing the Gemini language model from Google. Users can select the type and genre of the story, provide a prompt, and receive a continuation of the story. Additionally, the generated story can be converted into audio in various languages using Google's Text-to-Speech (gTTS) service.

Features:
Story Type Selection: Choose from different archetypes like overcoming the monster, rags to riches, the quest, voyage/journey and return, rebirth, tragedy, and comedy.
Genre Selection: Choose from genres such as fantasy, historical, fiction, horror, mystery, romance, science fiction, relationship fiction, suspense, thrillers, and action adventure.
Prompt Input: Provide a custom prompt to start the story.
Story Continuation: The app generates a continuation of the story based on the given prompt and selected options.
Audio Generation: Convert the generated story into audio in various languages.

Requirements:
Python 3.7 or higher,
Streamlit,
Google Generative AI,
LangChain,
gTTS,
pydantic,
typing.



Code Explanation:

configure_gemini_model(api_key: str):This function configures the Gemini model using the provided API key.

generate_gemini_text(prompt, model_name="gemini-1.5-flash"):This function generates text using the Gemini model based on the given prompt.

GeminiLLM:This class is a custom LLM (Language Learning Model) implementation for the Gemini model, compatible with LangChain's framework.

PromptTemplate:Defines a template for generating story continuations based on the given history, input, type, and genre.

ConversationBufferMemory:Stores the conversation history to provide context for generating story continuations.

LLMChain:Combines the LLM, prompt template, and memory to generate story continuations.

generate_story(story_type: str, genre: str, prompt: str) -> str:This function generates a story continuation based on the given type, genre, and prompt using the LLMChain.

Acknowledgements:
1.Google Generative AI: For providing the Gemini model.
2.Streamlit: For creating an easy-to-use web application framework.
3.gTTS: For converting text to speech.
