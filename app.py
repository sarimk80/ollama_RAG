import ollama
from pydantic import BaseModel
import pdfplumber
import chromadb
import streamlit as st
import asyncio
from streamlit_pdf_viewer import pdf_viewer
import nest_asyncio
import chromadb.api


data = []
table_data = []
embedd_result = ''



def ask_deepseek(prompt,data):
    response = ollama.chat(
        model = 'deepseek-r1:1.5b',
        messages=[
            {
                'role':'user',
                "content":f'Using this data: {data}. Respond to this prompt: {prompt}'
            }
            
        ]
    )
    print(response['message']['content'])

def prompt_input(collection):
    prompt = "WHY SHOULD AI MEET HUMAN “STUPIDITY”?"

    prompt_embedd = ollama.embed(
        model = 'nomic-embed-text:latest',
        input = prompt
    )
    result = collection.query(
        query_embeddings=prompt_embedd['embeddings'],
        n_results=2
    )

    

    # Safely access nested data
    if result is not None \
    and 'documents' in result \
    and isinstance(result['documents'], list) \
    and len(result['documents']) > 0 \
    and isinstance(result['documents'][0], list) \
    and len(result['documents'][0]) > 0:
        data = result['documents'][0][0]
        embedd_result = ' '.join(str(item) for sublist in data for item in sublist)
        ask_deepseek(prompt,embedd_result)
        
    else:
        data = None  # or raise an error/handle missing data
    
        

def emdedd_text(text,collection):
    for i , d in enumerate(text):

        embedd_response = ollama.embed(
            model='nomic-embed-text:latest',
            input= d
        )
        embeddings = embedd_response["embeddings"]
        collection.add(
            ids=[str(i)],
            embeddings=embeddings,
            documents=[d]
        )
        prompt_input(collection=collection)

def chunk_text(text,chunk_size=131000):
    words = text.split()
    return [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    

def read_pdf(collection):
    with pdfplumber.open('research_paper.pdf') as pdf:
        pages = pdf.pages
        for p in pages:
            data.append(p.extract_text())
            table_data.append(p.extract_table())
        chunk_of_text = chunk_text(''.join(data))
        emdedd_text(chunk_of_text,collection=collection)


def main(collection):
    st.set_page_config(layout="wide")
    st.title("Hello world")
    st.header("Upload research paper to ask questions and make power point presentation")
    col1, col2 = st.columns([0.6,0.4])

    with col1:
        uploaded_file = st.file_uploader('Choose your PDF file', type="pdf")
        if uploaded_file is not None:
            binary_data = uploaded_file.getvalue()
            pdf_viewer(input=binary_data,
                width=700)
    with col2:
        container = st.container(height=350,border=True)

        input_prompt = st.chat_input(placeholder="Enter message here")

if __name__== '__main__':
    client = chromadb.PersistentClient()
    client.clear_system_cache()
    client.delete_collection(name='docs')
    collection = client.create_collection(name="docs")

    import asyncio
    nest_asyncio.apply()
    main(collection=collection)
