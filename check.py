

User
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))






def get_pdf_text(pdf_docs):
    text=""
    for pdf in pdf_docs:
        pdf_reader= PdfReader(pdf)
        for page in pdf_reader.pages:
            text+= page.extract_text()
    return  text



def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks


def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")


def get_conversational_chain():

    prompt_template = """
    if they asked to create the question based on bloom taxonomy then 
    Based on the given context, generate questions for each level of Bloom's Taxonomy as follows:

    1) Remembering (Knowledge-based questions):
            Ask factual questions that require recalling information from the context.
            Sample question stems: Who, What, When, Where, Define, Identify, List, etc.
    2) Understanding (Comprehension-based questions):
            Ask questions that require understanding the meaning, interpreting, exemplifying, summarizing, or inferring information from the context.
            Sample question stems: Explain, Describe, Summarize, Illustrate, Interpret, etc.
    3) Applying (Application-based questions):
            Ask questions that require applying information from the context to new situations or solving problems.
            Sample question stems: How would you use/apply...? What would happen if...? Solve/Calculate, etc.
    4) Analyzing (Analysis-based questions):
            Ask questions that require breaking down information into parts, finding patterns, identifying causes/reasons, and making inferences.
            Sample question stems: Analyze, Differentiate, Categorize, Compare/Contrast, etc.
    5) Evaluating (Evaluation-based questions):
            Ask questions that require making judgments, evaluating ideas or solutions, and justifying decisions based on the context.
            Sample question stems: Evaluate, Justify, Critique, Argue for/against, etc.
    6) Creating (Synthesis-based questions):
            Ask questions that require generating new ideas, products, or ways of viewing things based on the context.
            Sample question stems: Design, Construct, Develop, Formulate, Propose, etc. 
    
    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro",
                             temperature=0.3)

    prompt = PromptTemplate(template = prompt_template, input_variables = ["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain



def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
    
    new_db = FAISS.load_local("faiss_index", embeddings)
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()

    
    response = chain(
        {"input_documents":docs, "question": user_question}
        , return_only_outputs=True)

    print(response)
    st.write("Reply: ", response["output_text"])




def main():
    st.set_page_config("Chat PDF")
    st.header("Chat with PDF using Gemini💁")

    user_question =  "genetate questions based on bloom taxonomy"

    if user_question:
        user_input(user_question)

    with st.sidebar:
        st.title("Menu:")
        pdf_docs = st.file_uploader("Upload your PDF Files and Click on the Submit & Process Button", accept_multiple_files=True)
        if st.button("Submit & Process"):
            with st.spinner("Processing..."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                get_vector_store(text_chunks)
                st.success("Done")



if __name__ == "__main__":
    main()