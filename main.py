from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from groq import Groq
import PyPDF2
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY")

st.markdown("""
<style>
.big-font {
    font-size:30px !important;
}
</style>
""", unsafe_allow_html=True)

st.write("")

st.markdown('<p class="big-font">Hello buddy! I\'m C2MA [Custom Cold Mail Assist]</p>', unsafe_allow_html=True)
job_url = st.text_input("Enter the Job URL")
uploaded_pdf = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])

if job_url and uploaded_pdf:
    loader = WebBaseLoader(job_url)
    page_data = loader.load().pop().page_content 

    with uploaded_pdf:
        reader = PyPDF2.PdfReader(uploaded_pdf)
        all_text = ""
        for page in range(len(reader.pages)):
            page_text = reader.pages[page].extract_text()
            all_text += page_text

    prompt = PromptTemplate.from_template(
        """
        ### SCRAPED TEXT FROM WEBSITE:
        {page_data}
        ### INSTRUCTION:
        The scraped text is from the career's page of a website.
        Your job is to extract the job postings for the USER, based on their background, and return them in JSON format containing the
        following keys: `role`, `experience`, `skills`, and `description`.
        ### VALID JSON (NO PREAMBLE):
        """
    )

    res = prompt.format(page_data=page_data)

    email_prompt = f"""
    Write a professional cold email to apply for the following job. Use the user's details to highlight their relevant experience and skills.NO PREAMBLE

    ### Job Description:
    {res}

    ### User Information:
    {all_text}

    The email should:
    1. Start with a polite and professional greeting.
    2. Introduce the user (Vignesh R) and mention the job role being applied for.
    3. Highlight Vignesh's relevant skills, experience, and why he's a great fit for the role.
    4. Express enthusiasm for the opportunity and willingness to contribute to the team.
    5. End with a polite closing, contact information as email [vigneshraiml@gmail.com].
    6. Make it as short and informative as possible.

    Be sure to keep the tone professional and concise, and avoid any false information.
    """

    client = Groq(api_key=api_key) 
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": email_prompt,
            }
        ],
        model="llama3-8b-8192",
    )

    generated_email = chat_completion.choices[0].message.content
    st.subheader("Generated Cold Email:")
    st.write(generated_email)
else:
    st.write("Please provide both a job URL and a PDF resume to generate a cold email.")
