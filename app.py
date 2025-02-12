import ollama
from pydantic import BaseModel
import pdfplumber
import chromadb
import streamlit as st
import asyncio
from streamlit_pdf_viewer import pdf_viewer
import nest_asyncio
import chromadb.api
import re


data = []
table_data = []
embedd_result = ''
result = ''

client = chromadb.PersistentClient()
client.clear_system_cache()
client.delete_collection(name='docs')
collection = client.create_collection(name="docs")


def ask_deepseek(prompt,embedResult):
    print(prompt)
    response = ollama.chat(
        model = 'llama3.2:3b',
        messages=[
            {
                'role':'user',
                'content':f"""
                Using this data: {embedResult}. Respond to this prompt: {prompt}
                 """
                
            },
            
            
        ]
    )
    result = response['message']['content']
    print(response['message']['content'])

def prompt_input(inputPrompt):
    prompt = inputPrompt

    prompt_embedd = ollama.embed(
        model = 'nomic-embed-text:latest',
        input = prompt
    )
    result = collection.query(
        query_embeddings=prompt_embedd['embeddings'],
        n_results=5
    )
    

    # Safely access nested data
    if result is not None \
    and 'documents' in result \
    and isinstance(result['documents'], list) \
    and len(result['documents']) > 0 \
    and isinstance(result['documents'][0], list) \
    and len(result['documents'][0]) > 0:
        data = result['documents'][0][0]
        print("THIS IS DATA FROM COLLECTION")
        embedd_result = ' '.join(str(item) for sublist in data for item in sublist)
        ask_deepseek(prompt,data)
        
    else:
        data = None  # or raise an error/handle missing data
    
        

def emdedd_text(text):
    for i , d in enumerate(text):
        print(d)
        embedd_response = ollama.embed(
            model='nomic-embed-text:latest',
            input= d
        )
        embeddings = embedd_response["embeddings"]
        collection.add(
            ids=[str(i)],
            embeddings = embeddings,
            documents=[d]
        )
        #prompt_input(collection=collection)
    print('All text is embedded')

def chunk_text(text,chunk_size=2000):
    words = text.split()
    return [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    


def read_pdf(uploaded_file):
    cleaned_text = ''

#def read_pdf(collection):
    #with pdfplumber.open('research_paper.pdf') as pdf:

    with pdfplumber.open(uploaded_file) as pdf:
        pages = pdf.pages
        for p in pages:
            text = p.extract_text()
            if text:
                if "Bibliography" in text or "References" in text or "Works Cited" in text:
                    break
                cleaned_text += text + "\n"
                data.append(cleaned_text)
            table_data.append(p.extract_table())
        chunk_of_text = chunk_text(''.join(data))
        
        print("Read pdf done")
        emdedd_text(chunk_of_text)
        print("Ready to ask question")
        


def inputAndOutputUI(collection):
    container = st.container(height=400,border=True)

    input_prompt = st.chat_input(placeholder="Enter message here")
    if input_prompt:
        prompt_input(inputPrompt=input_prompt)



def main(collection):
    st.set_page_config(layout="wide")
    st.header("Upload research paper to ask questions and make power point presentation")
    col1, col2 = st.columns([0.4,0.6])

    with col1:
        uploaded_file = st.file_uploader('Choose your PDF file', type="pdf")
        if uploaded_file is not None:
            binary_data = uploaded_file.getvalue()
            pdf_viewer(input=binary_data,
                width=550)
            read_pdf(uploaded_file)
    with col2:
        inputAndOutputUI(collection=collection)
        

if __name__== '__main__':
    # client = chromadb.PersistentClient()
    # client.clear_system_cache()
    # client.delete_collection(name='docs')
    # collection = client.create_collection(name="docs")

    import asyncio
    nest_asyncio.apply()
    main(collection=collection)
